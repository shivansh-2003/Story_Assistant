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
    StoryResponse, EditResponse, AudioRequest, PDFRequest, StoryTheme, StoryCreationRequest,
    Chapter, ChapterRequest, ChapterResponse, ChapterStatus, Relationship, RelationshipRequest,
    StoryUpdateRequest
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
    character_data = character.model_dump()
    created_character = story_manager.create_character(character_data)
    return {
        "success": True,
        "character": created_character,
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

# Extended Character Management Endpoints
@app.get("/characters/", response_model=dict)
async def list_characters():
    """List all characters"""
    characters = story_manager.get_all_characters()
    return {
        "success": True,
        "characters": characters,
        "count": len(characters),
        "message": "Characters retrieved successfully"
    }

@app.get("/characters/{character_id}", response_model=dict)
async def get_character(character_id: str):
    """Get specific character"""
    character = story_manager.get_character(character_id)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    return {
        "success": True,
        "character": character,
        "message": "Character retrieved successfully"
    }

@app.put("/characters/{character_id}", response_model=dict)
async def update_character(character_id: str, character_data: dict):
    """Update existing character"""
    success = story_manager.update_character(character_id, **character_data)
    if not success:
        raise HTTPException(status_code=404, detail="Character not found")
    
    updated_character = story_manager.get_character(character_id)
    return {
        "success": True,
        "character": updated_character,
        "message": "Character updated successfully"
    }

@app.delete("/characters/{character_id}", response_model=dict)
async def delete_character(character_id: str):
    """Delete character"""
    success = story_manager.delete_character(character_id)
    if not success:
        raise HTTPException(status_code=404, detail="Character not found")
    
    return {
        "success": True,
        "message": "Character deleted successfully"
    }

# Enhanced Story Management Endpoints
@app.put("/stories/{story_id}", response_model=StoryResponse)
async def update_story(story_id: str, update_data: StoryUpdateRequest):
    """Update story details"""
    story = story_manager.get_story(story_id)
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    
    update_dict = update_data.model_dump(exclude_unset=True)
    success = story_manager.update_story(story_id, **update_dict)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update story")
    
    updated_story = story_manager.get_story(story_id)
    return StoryResponse(
        success=True,
        story=updated_story,
        message="Story updated successfully"
    )

@app.delete("/stories/{story_id}", response_model=dict)
async def delete_story(story_id: str):
    """Delete story"""
    success = story_manager.delete_story(story_id)
    if not success:
        raise HTTPException(status_code=404, detail="Story not found")
    
    return {
        "success": True,
        "message": "Story deleted successfully"
    }

# Chapter Management Endpoints
@app.get("/stories/{story_id}/chapters/", response_model=dict)
async def get_story_chapters(story_id: str):
    """Get all chapters for a story"""
    story = story_manager.get_story(story_id)
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    
    chapters = story_manager.get_story_chapters(story_id)
    return {
        "success": True,
        "chapters": chapters,
        "count": len(chapters),
        "message": "Chapters retrieved successfully"
    }

@app.post("/stories/{story_id}/chapters/", response_model=ChapterResponse)
async def create_chapter(story_id: str, chapter_data: ChapterRequest):
    """Create new chapter"""
    chapter = story_manager.create_chapter(
        story_id=story_id,
        title=chapter_data.title,
        content=chapter_data.content or "",
        status=chapter_data.status or ChapterStatus.DRAFT
    )
    
    if not chapter:
        raise HTTPException(status_code=404, detail="Story not found")
    
    return ChapterResponse(
        success=True,
        chapter=chapter,
        message="Chapter created successfully"
    )

@app.get("/stories/{story_id}/chapters/{chapter_id}", response_model=ChapterResponse)
async def get_chapter(story_id: str, chapter_id: str):
    """Get specific chapter"""
    chapter = story_manager.get_chapter(story_id, chapter_id)
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    
    return ChapterResponse(
        success=True,
        chapter=chapter,
        message="Chapter retrieved successfully"
    )

@app.put("/stories/{story_id}/chapters/{chapter_id}", response_model=ChapterResponse)
async def update_chapter(story_id: str, chapter_id: str, chapter_data: ChapterRequest):
    """Update chapter"""
    update_dict = chapter_data.model_dump(exclude_unset=True)
    success = story_manager.update_chapter(story_id, chapter_id, **update_dict)
    
    if not success:
        raise HTTPException(status_code=404, detail="Chapter not found")
    
    updated_chapter = story_manager.get_chapter(story_id, chapter_id)
    return ChapterResponse(
        success=True,
        chapter=updated_chapter,
        message="Chapter updated successfully"
    )

@app.delete("/stories/{story_id}/chapters/{chapter_id}", response_model=dict)
async def delete_chapter(story_id: str, chapter_id: str):
    """Delete chapter"""
    print(f"DEBUG: FastAPI delete_chapter called with story_id={story_id}, chapter_id={chapter_id}")
    success = story_manager.delete_chapter(story_id, chapter_id)
    print(f"DEBUG: story_manager.delete_chapter returned: {success}")
    if not success:
        raise HTTPException(status_code=404, detail="Chapter not found")
    
    return {
        "success": True,
        "message": "Chapter deleted successfully"
    }

# Chapter Generation Endpoint
@app.post("/stories/{story_id}/chapters/{chapter_id}/generate/", response_model=ChapterResponse)
async def generate_chapter_content(story_id: str, chapter_id: str, target_length: str = "medium"):
    """Generate AI content for a chapter"""
    try:
        # Get story and chapter
        story = story_manager.get_story(story_id)
        if not story:
            raise HTTPException(status_code=404, detail="Story not found")
        
        chapter = story_manager.get_chapter(story_id, chapter_id)
        if not chapter:
            raise HTTPException(status_code=404, detail="Chapter not found")
        
        if llm_service_instance is None:
            raise HTTPException(status_code=500, detail="LLM service not initialized")
        
        # Get story context from previous chapters
        story_context = ""
        sorted_chapters = sorted(story.chapters, key=lambda x: x.order)
        for ch in sorted_chapters:
            if ch.order < chapter.order and ch.content:
                story_context += f"\n{ch.title}:\n{ch.content}\n"
        
        # If no previous context, use story idea
        if not story_context.strip():
            story_context = f"Story Premise: {story.base_idea}"
        
        # Generate chapter content
        generated_content = llm_service_instance.generate_chapter_content(
            chapter_title=chapter.title,
            story_context=story_context,
            characters=story.characters,
            theme=story.theme,
            target_length=target_length
        )
        
        # Update chapter with generated content
        success = story_manager.update_chapter(
            story_id, 
            chapter_id, 
            content=generated_content,
            status=ChapterStatus.DRAFT
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update chapter")
        
        updated_chapter = story_manager.get_chapter(story_id, chapter_id)
        return ChapterResponse(
            success=True,
            chapter=updated_chapter,
            message="Chapter content generated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Chapter generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chapter generation failed: {str(e)}")

# Relationship Management Endpoints
@app.get("/relationships/", response_model=dict)
async def list_relationships():
    """List all character relationships"""
    relationships = story_manager.get_all_relationships()
    return {
        "success": True,
        "relationships": relationships,
        "count": len(relationships),
        "message": "Relationships retrieved successfully"
    }

@app.post("/relationships/", response_model=dict)
async def create_relationship(relationship_data: RelationshipRequest):
    """Create character relationship"""
    # Verify characters exist
    char1 = story_manager.get_character(relationship_data.character1_id)
    char2 = story_manager.get_character(relationship_data.character2_id)
    
    if not char1 or not char2:
        raise HTTPException(status_code=404, detail="One or both characters not found")
    
    relationship = story_manager.create_relationship(
        character1_id=relationship_data.character1_id,
        character2_id=relationship_data.character2_id,
        relationship_type=relationship_data.type,
        description=relationship_data.description,
        strength=relationship_data.strength
    )
    
    return {
        "success": True,
        "relationship": relationship,
        "message": "Relationship created successfully"
    }

@app.get("/relationships/{relationship_id}", response_model=dict)
async def get_relationship(relationship_id: str):
    """Get specific relationship"""
    relationship = story_manager.get_relationship(relationship_id)
    if not relationship:
        raise HTTPException(status_code=404, detail="Relationship not found")
    
    return {
        "success": True,
        "relationship": relationship,
        "message": "Relationship retrieved successfully"
    }

@app.put("/relationships/{relationship_id}", response_model=dict)
async def update_relationship(relationship_id: str, relationship_data: RelationshipRequest):
    """Update relationship"""
    update_dict = relationship_data.model_dump(exclude_unset=True)
    success = story_manager.update_relationship(relationship_id, **update_dict)
    
    if not success:
        raise HTTPException(status_code=404, detail="Relationship not found")
    
    updated_relationship = story_manager.get_relationship(relationship_id)
    return {
        "success": True,
        "relationship": updated_relationship,
        "message": "Relationship updated successfully"
    }

@app.delete("/relationships/{relationship_id}", response_model=dict)
async def delete_relationship(relationship_id: str):
    """Delete relationship"""
    success = story_manager.delete_relationship(relationship_id)
    if not success:
        raise HTTPException(status_code=404, detail="Relationship not found")
    
    return {
        "success": True,
        "message": "Relationship deleted successfully"
    }

@app.get("/characters/{character_id}/relationships/", response_model=dict)
async def get_character_relationships(character_id: str):
    """Get all relationships for a character"""
    character = story_manager.get_character(character_id)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    relationships = story_manager.get_character_relationships(character_id)
    return {
        "success": True,
        "relationships": relationships,
        "count": len(relationships),
        "message": "Character relationships retrieved successfully"
    }

# Draft Management Endpoints
@app.post("/stories/{story_id}/draft/", response_model=dict)
async def save_story_draft(story_id: str):
    """Save story as draft"""
    success = story_manager.update_story(story_id, is_draft=True)
    if not success:
        raise HTTPException(status_code=404, detail="Story not found")
    
    return {
        "success": True,
        "message": "Story saved as draft"
    }

@app.get("/drafts/", response_model=dict)
async def list_drafts():
    """List all draft stories"""
    all_stories = list(story_manager.stories.values())
    drafts = [story for story in all_stories if story.is_draft]
    
    return {
        "success": True,
        "drafts": drafts,
        "count": len(drafts),
        "message": "Draft stories retrieved successfully"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)