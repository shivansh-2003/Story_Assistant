from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import Response
from contextlib import asynccontextmanager
import os
from typing import List, Optional

# Try to load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not installed, continue without it
    pass

from models import (
    Character, Story, StoryGenerationRequest, StoryEditRequest,
    StoryResponse, EditResponse, AudioRequest, PDFRequest, StoryTheme, StoryCreationRequest
)
from story_manager import story_manager
from llm_service import initialize_llm_service
import llm_service
from story_workflow import story_workflow
from export_services import pdf_service, audio_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        print("⚠️  Warning: GROQ_API_KEY environment variable not set.")
        print("   🔄 Using Mock LLM Service for development/testing.")
        print("   ℹ️  Get your API key from: https://console.groq.com/keys")
        initialize_llm_service(None)  # Will use mock service
    else:
        try:
            initialize_llm_service(groq_api_key)
            print("✅ LLM service initialized successfully with Groq API")
        except Exception as e:
            print(f"❌ Failed to initialize LLM service: {e}")
            print("🔄 Falling back to Mock LLM Service")
            initialize_llm_service(None)  # Fallback to mock
    
    yield
    # Shutdown
    print("🔄 Shutting down...")

app = FastAPI(
    title="Interactive Storytelling API", 
    version="1.0.0",
    lifespan=lifespan
)

# Initialize LLM service on startup
# @app.on_event("startup")
# async def startup_event():
#     groq_api_key = os.getenv("GROQ_API_KEY")
#     if not groq_api_key:
#         raise ValueError("GROQ_API_KEY environment variable is required")
#     initialize_llm_service(groq_api_key)

# Character Management Endpoints
@app.post("/characters/", response_model=dict)
async def create_character(character: Character):
    """Create a new character"""
    return {
        "success": True,
        "character": character,
        "message": "Character created successfully"
    }

@app.post("/characters/backstory/", response_model=dict)
async def generate_character_backstory(character: Character):
    """Generate backstory for a character"""
    try:
        backstory = llm_service.llm_service.generate_character_backstory(character)
        character.backstory = backstory
        return {
            "success": True,
            "character": character,
            "backstory": backstory,
            "message": "Backstory generated successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Story Management Endpoints
@app.post("/stories/", response_model=StoryResponse)
async def create_story(request: StoryCreationRequest):
    """Create a new story"""
    try:
        story = story_manager.create_story(request.base_idea, request.theme, request.characters or [])
        return StoryResponse(
            success=True,
            story=story,
            message="Story created successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stories/{story_id}", response_model=StoryResponse)
async def get_story(story_id: str):
    """Get story by ID"""
    story = story_manager.get_story(story_id)
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    
    return StoryResponse(
        success=True,
        story=story,
        message="Story retrieved successfully"
    )

@app.post("/stories/{story_id}/characters/", response_model=dict)
async def add_character_to_story(story_id: str, character: Character):
    """Add character to story"""
    success = story_manager.add_character(story_id, character)
    if not success:
        raise HTTPException(status_code=400, detail="Cannot add character (story not found or max characters reached)")
    
    return {
        "success": True,
        "message": f"Character {character.name} added to story"
    }

@app.post("/stories/{story_id}/complete/", response_model=dict)
async def complete_story(story_id: str):
    """Mark story as completed"""
    success = story_manager.complete_story(story_id)
    if not success:
        raise HTTPException(status_code=404, detail="Story not found")
    
    return {
        "success": True,
        "message": "Story marked as completed"
    }

# Story Generation Endpoints
@app.post("/stories/generate/", response_model=StoryResponse)
async def generate_story_segment(request: StoryGenerationRequest):
    """Generate new story segment"""
    try:
        # Get story to validate it exists
        story = story_manager.get_story(request.story_id)
        if not story:
            raise HTTPException(status_code=404, detail="Story not found")
        
        # Use workflow to generate content
        result = story_workflow.generate_story_segment(
            story_id=request.story_id,
            theme=request.theme,
            characters=request.characters,
            previous_content=request.previous_content,
            user_choice=request.user_choice,
            auto_continue=request.auto_continue
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("error", "Generation failed"))
        
        # Add segment to story
        new_segment = story_manager.add_segment(request.story_id, result["content"])
        
        return StoryResponse(
            success=True,
            story=story_manager.get_story(request.story_id),
            new_segment=new_segment,
            message="Story segment generated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Story Editing Endpoints
@app.post("/stories/edit/", response_model=EditResponse)
async def edit_story_segment(request: StoryEditRequest):
    """Edit existing story segment"""
    try:
        # Get the segment to edit
        segment = story_manager.get_segment(request.story_id, request.segment_id)
        if not segment:
            raise HTTPException(status_code=404, detail="Segment not found")
        
        # Get context for editing
        context = story_manager.get_context_for_segment(request.story_id, request.segment_id)
        
        # Use workflow to edit content
        result = story_workflow.edit_story_segment(
            story_id=request.story_id,
            current_segment=request.original_content,
            edit_instruction=request.edit_instruction,
            context=context,
            characters=request.characters
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("error", "Edit failed"))
        
        # Update segment in story
        success = story_manager.edit_segment(
            request.story_id, 
            request.segment_id, 
            result["edited_content"]
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update segment")
        
        return EditResponse(
            success=True,
            original_content=result["original_content"],
            edited_content=result["edited_content"],
            segment_id=request.segment_id,
            message="Segment edited successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Export Endpoints
@app.post("/stories/{story_id}/export/pdf/")
async def export_story_to_pdf(story_id: str):
    """Export story to PDF"""
    story = story_manager.get_story(story_id)
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    
    try:
        pdf_bytes = pdf_service.create_basic_pdf(story)
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=story_{story_id}.pdf"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")

@app.post("/stories/{story_id}/export/pdf/base64/")
async def export_story_to_pdf_base64(story_id: str):
    """Export story to PDF as base64"""
    story = story_manager.get_story(story_id)
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    
    try:
        pdf_base64 = pdf_service.create_pdf_base64(story)
        return {
            "success": True,
            "pdf_base64": pdf_base64,
            "filename": f"story_{story_id}.pdf"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")

@app.post("/stories/{story_id}/export/audio/")
async def export_story_to_audio(story_id: str, language: str = "en"):
    """Export story to audio"""
    story = story_manager.get_story(story_id)
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    
    try:
        audio_bytes = audio_service.create_audio_from_story(story, language)
        
        return Response(
            content=audio_bytes,
            media_type="audio/mpeg",
            headers={"Content-Disposition": f"attachment; filename=story_{story_id}.mp3"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audio generation failed: {str(e)}")

@app.post("/stories/{story_id}/export/audio/base64/")
async def export_story_to_audio_base64(story_id: str, language: str = "en"):
    """Export story to audio as base64"""
    story = story_manager.get_story(story_id)
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    
    try:
        audio_base64 = audio_service.create_audio_base64(story, language)
        return {
            "success": True,
            "audio_base64": audio_base64,
            "filename": f"story_{story_id}.mp3",
            "language": language
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audio generation failed: {str(e)}")

@app.get("/export/audio/languages/")
async def get_supported_audio_languages():
    """Get supported audio languages"""
    return {
        "success": True,
        "languages": audio_service.get_supported_languages()
    }

# Utility Endpoints
@app.get("/health/")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "Interactive Storytelling API is running"
    }

@app.get("/stories/")
async def list_stories():
    """List all stories (for development)"""
    return {
        "success": True,
        "stories": list(story_manager.stories.keys()),
        "count": len(story_manager.stories)
    }
@app.get("/debug/llm/")
async def debug_llm_service():
    """Debug LLM service status"""
    return {
        "llm_service_type": type(llm_service.llm_service).__name__ if llm_service.llm_service else "None",
        "llm_service_is_none": llm_service.llm_service is None,
        "has_generate_method": hasattr(llm_service.llm_service, 'generate_character_backstory') if llm_service.llm_service else False
    }
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)