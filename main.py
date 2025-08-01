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
from export_services import pdf_service, audio_service

# Global LLM service instance
llm_service_instance = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting Interactive Storytelling API...")
    
    # Check for API key
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        print("❌ GROQ_API_KEY environment variable is not set!")
        print("Please set your Groq API key:")
        print("export GROQ_API_KEY='your_api_key_here'")
        raise ValueError("GROQ_API_KEY is required")
    
    print(f"🔍 GROQ_API_KEY found: {groq_api_key[:10]}...")
    
    # Initialize the LLM service
    try:
        global llm_service_instance
        llm_service_instance = initialize_llm_service()
        print(f"✅ LLM service ready: {type(llm_service_instance).__name__}")
        
        # Test the service
        from models import Character, PersonalityType
        test_char = Character(
            name="TestChar", 
            primary_trait=PersonalityType.BRAVE, 
            appearance="Test appearance"
        )
        test_result = llm_service_instance.generate_character_backstory(test_char)
        print("🧪 LLM service test successful")
        
    except Exception as e:
        print(f"❌ Failed to initialize LLM service: {e}")
        raise e
    
    yield
    # Shutdown
    print("🔄 Shutting down...")

app = FastAPI(
    title="Interactive Storytelling API", 
    version="1.0.0",
    lifespan=lifespan
)

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
        if llm_service_instance is None:
            raise HTTPException(status_code=500, detail="LLM service not initialized")
        
        backstory = llm_service_instance.generate_character_backstory(character)
        character.backstory = backstory
        return {
            "success": True,
            "character": character,
            "backstory": backstory,
            "message": "Backstory generated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Backstory generation error: {str(e)}")
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
        
        if llm_service_instance is None:
            raise HTTPException(status_code=500, detail="LLM service not initialized")
        
        # Generate content directly using LLM service (bypassing problematic workflow)
        try:
            # Generate story content directly
            if request.auto_continue:
                content = llm_service_instance.generate_story_continuation(
                    theme=request.theme,
                    characters=request.characters,
                    previous_content=request.previous_content,
                    user_choice=None,
                    auto_continue=True
                )
            else:
                content = llm_service_instance.generate_story_continuation(
                    theme=request.theme,
                    characters=request.characters,
                    previous_content=request.previous_content,
                    user_choice=request.user_choice,
                    auto_continue=False
                )
            
            # Add segment to story
            new_segment = story_manager.add_segment(request.story_id, content)
            
        except Exception as generation_error:
            print(f"Generation error: {generation_error}")
            raise HTTPException(status_code=500, detail=f"Generation failed: {str(generation_error)}")
        
        return StoryResponse(
            success=True,
            story=story_manager.get_story(request.story_id),
            new_segment=new_segment,
            message="Story segment generated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Story generation error: {str(e)}")
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
        
        if llm_service_instance is None:
            raise HTTPException(status_code=500, detail="LLM service not initialized")
        
        # Get context for editing
        context = story_manager.get_context_for_segment(request.story_id, request.segment_id)
        
        # Edit content directly using LLM service (bypassing problematic workflow)
        try:
            edited_content = llm_service_instance.edit_story_segment(
                original_content=request.original_content,
                edit_instruction=request.edit_instruction,
                context=context,
                characters=request.characters
            )
            
            # Update segment in story
            success = story_manager.edit_segment(
                request.story_id, 
                request.segment_id, 
                edited_content
            )
            
            if not success:
                raise HTTPException(status_code=500, detail="Failed to update segment")
            
        except Exception as edit_error:
            print(f"Edit error: {edit_error}")
            raise HTTPException(status_code=500, detail=f"Edit failed: {str(edit_error)}")
        
        return EditResponse(
            success=True,
            original_content=request.original_content,
            edited_content=edited_content,
            segment_id=request.segment_id,
            message="Segment edited successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Story edit error: {str(e)}")
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
        print(f"PDF export error: {str(e)}")
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
        print(f"PDF base64 export error: {str(e)}")
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
        "llm_service_type": type(llm_service_instance).__name__ if llm_service_instance else "None",
        "llm_service_is_none": llm_service_instance is None,
        "has_generate_method": hasattr(llm_service_instance, 'generate_character_backstory') if llm_service_instance else False,
        "groq_api_key_set": bool(os.getenv("GROQ_API_KEY"))
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)