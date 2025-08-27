# api/routes.py
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, Query
from typing import Dict, Any, List, Optional, Union
import uuid
import asyncio
import logging
from datetime import datetime

from models.story_models import (
    Story, StoryCreate, StoryUpdate, StoryWithChapters,
    Chapter, ChapterCreate, ChapterUpdate, ChapterWithSegments,
    ContentGenerationRequest, ChapterGenerationRequest, SegmentGenerationRequest,
    GenerationResponse, GenerationResult
)
from models.character_models import (
    Character, CharacterCreate, CharacterUpdate, CharacterWithRelationships,
    CharacterRelationship, CharacterRelationshipCreate,
    CharacterGenerationRequest, CharacterGenerationResult
)
from models.generation_models import (
    GenerationTask, GenerationTaskCreate, GenerationTaskUpdate,
    ImageGenerationRequest, ImageGenerationResult,
    PosterGenerationRequest, PosterGenerationResult,
    StoryContext, AgentContext, GenerationType
)
from workflows.story_generation_workflow import execute_story_generation
from workflows.chapter_continuation_workflow import execute_chapter_continuation
from services.vector_service import get_vector_service
from services.llm_service import get_llm_service
from services.image_service import get_image_service
from api.dependencies import get_current_user, get_supabase_client

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# ===== STORY MANAGEMENT ROUTES =====

@router.post("/stories", response_model=Story)
async def create_story(
    story: StoryCreate,
    current_user: Dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """Create a new story"""
    try:
        story_data = story.dict()
        story_data["user_id"] = current_user["id"]
        
        result = supabase.table("stories").insert(story_data).execute()
        
        if result.data:
            return Story(**result.data[0])
        else:
            raise HTTPException(status_code=400, detail="Failed to create story")
            
    except Exception as e:
        logger.error(f"Failed to create story: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stories", response_model=List[Story])
async def get_user_stories(
    current_user: Dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Get user's stories with pagination"""
    try:
        result = supabase.table("stories")\
            .select("*")\
            .eq("user_id", current_user["id"])\
            .range(offset, offset + limit - 1)\
            .order("updated_at", desc=True)\
            .execute()
        
        return [Story(**story) for story in result.data]
        
    except Exception as e:
        logger.error(f"Failed to get stories: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stories/{story_id}", response_model=StoryWithChapters)
async def get_story_with_chapters(
    story_id: str,
    current_user: Dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """Get story with all chapters"""
    try:
        # Get story
        story_result = supabase.table("stories")\
            .select("*")\
            .eq("id", story_id)\
            .eq("user_id", current_user["id"])\
            .execute()
        
        if not story_result.data:
            raise HTTPException(status_code=404, detail="Story not found")
        
        story = Story(**story_result.data[0])
        
        # Get chapters
        chapters_result = supabase.table("chapters")\
            .select("*")\
            .eq("story_id", story_id)\
            .order("chapter_order")\
            .execute()
        
        chapters = [Chapter(**chapter) for chapter in chapters_result.data]
        
        return StoryWithChapters(**story.dict(), chapters=chapters)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get story: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/stories/{story_id}", response_model=Story)
async def update_story(
    story_id: str,
    story_update: StoryUpdate,
    current_user: Dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """Update story"""
    try:
        update_data = story_update.dict(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow().isoformat()
        
        result = supabase.table("stories")\
            .update(update_data)\
            .eq("id", story_id)\
            .eq("user_id", current_user["id"])\
            .execute()
        
        if result.data:
            return Story(**result.data[0])
        else:
            raise HTTPException(status_code=404, detail="Story not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update story: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/stories/{story_id}")
async def delete_story(
    story_id: str,
    current_user: Dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """Delete story and all related data"""
    try:
        result = supabase.table("stories")\
            .delete()\
            .eq("id", story_id)\
            .eq("user_id", current_user["id"])\
            .execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Story not found")
        
        return {"message": "Story deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete story: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== CHAPTER MANAGEMENT ROUTES =====

@router.post("/stories/{story_id}/chapters", response_model=Chapter)
async def create_chapter(
    story_id: str,
    chapter: ChapterCreate,
    current_user: Dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """Create a new chapter"""
    try:
        # Verify story ownership
        story_result = supabase.table("stories")\
            .select("id")\
            .eq("id", story_id)\
            .eq("user_id", current_user["id"])\
            .execute()
        
        if not story_result.data:
            raise HTTPException(status_code=404, detail="Story not found")
        
        chapter_data = chapter.dict()
        chapter_data["story_id"] = story_id
        
        result = supabase.table("chapters").insert(chapter_data).execute()
        
        if result.data:
            return Chapter(**result.data[0])
        else:
            raise HTTPException(status_code=400, detail="Failed to create chapter")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create chapter: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stories/{story_id}/chapters/{chapter_id}", response_model=ChapterWithSegments)
async def get_chapter_with_segments(
    story_id: str,
    chapter_id: str,
    current_user: Dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """Get chapter with all segments"""
    try:
        # Verify access
        story_result = supabase.table("stories")\
            .select("id")\
            .eq("id", story_id)\
            .eq("user_id", current_user["id"])\
            .execute()
        
        if not story_result.data:
            raise HTTPException(status_code=404, detail="Story not found")
        
        # Get chapter
        chapter_result = supabase.table("chapters")\
            .select("*")\
            .eq("id", chapter_id)\
            .eq("story_id", story_id)\
            .execute()
        
        if not chapter_result.data:
            raise HTTPException(status_code=404, detail="Chapter not found")
        
        chapter = Chapter(**chapter_result.data[0])
        
        # Get segments
        segments_result = supabase.table("chapter_segments")\
            .select("*")\
            .eq("chapter_id", chapter_id)\
            .order("segment_order")\
            .execute()
        
        segments = [ChapterSegment(**segment) for segment in segments_result.data]
        
        return ChapterWithSegments(**chapter.dict(), segments=segments)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get chapter: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== CONTENT GENERATION ROUTES =====

@router.post("/stories/{story_id}/generate", response_model=GenerationResponse)
async def generate_story_content(
    story_id: str,
    request: ContentGenerationRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """Generate story content using the multi-agent workflow"""
    try:
        # Verify story ownership
        story_result = supabase.table("stories")\
            .select("*")\
            .eq("id", story_id)\
            .eq("user_id", current_user["id"])\
            .execute()
        
        if not story_result.data:
            raise HTTPException(status_code=404, detail="Story not found")
        
        story = Story(**story_result.data[0])
        
        # Get characters
        characters_result = supabase.table("story_characters")\
            .select("*, characters(*)")\
            .eq("story_id", story_id)\
            .execute()
        
        characters = [rel["characters"] for rel in characters_result.data if rel["characters"]]
        
        # Create task
        task_id = str(uuid.uuid4())
        
        task_data = GenerationTaskCreate(
            user_id=uuid.UUID(current_user["id"]),
            task_type=GenerationType.CHAPTER,
            task_data={
                "story_id": story_id,
                "generation_request": request.dict(),
                "user_id": current_user["id"]
            }
        )
        
        # Store task in database
        task_result = supabase.table("generation_tasks")\
            .insert(task_data.dict())\
            .execute()
        
        if not task_result.data:
            raise HTTPException(status_code=500, detail="Failed to create generation task")
        
        # Create story context
        story_context = StoryContext(
            story_id=uuid.UUID(story_id),
            current_chapter_id=request.chapter_id,
            story_metadata=story.dict(),
            generation_settings=story.generation_settings,
            image_settings=story.image_settings,
            characters=characters,
            world_elements=[],
            previous_content="",  # Would be populated from existing chapters
            continuation_context={}
        )
        
        # Start background generation
        background_tasks.add_task(
            _execute_generation_workflow,
            task_id,
            story_context,
            request.user_input or "",
            request.dict(),
            supabase
        )
        
        return GenerationResponse(
            task_id=task_id,
            status="processing",
            message="Story generation started",
            estimated_completion_time=60
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stories/{story_id}/chapters/{chapter_id}/continue", response_model=GenerationResponse)
async def continue_chapter(
    story_id: str,
    chapter_id: str,
    request: SegmentGenerationRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """Continue an existing chapter with new segments"""
    try:
        # Verify access and get data
        story_result = supabase.table("stories")\
            .select("*")\
            .eq("id", story_id)\
            .eq("user_id", current_user["id"])\
            .execute()
        
        if not story_result.data:
            raise HTTPException(status_code=404, detail="Story not found")
        
        chapter_result = supabase.table("chapters")\
            .select("*")\
            .eq("id", chapter_id)\
            .eq("story_id", story_id)\
            .execute()
        
        if not chapter_result.data:
            raise HTTPException(status_code=404, detail="Chapter not found")
        
        story = Story(**story_result.data[0])
        chapter = Chapter(**chapter_result.data[0])
        
        # Get characters
        characters_result = supabase.table("story_characters")\
            .select("*, characters(*)")\
            .eq("story_id", story_id)\
            .execute()
        
        characters = [rel["characters"] for rel in characters_result.data if rel["characters"]]
        
        # Create task
        task_id = str(uuid.uuid4())
        
        task_data = GenerationTaskCreate(
            user_id=uuid.UUID(current_user["id"]),
            task_type=GenerationType.SEGMENT,
            task_data={
                "story_id": story_id,
                "chapter_id": chapter_id,
                "continuation_request": request.dict(),
                "user_id": current_user["id"]
            }
        )
        
        # Store task
        task_result = supabase.table("generation_tasks")\
            .insert(task_data.dict())\
            .execute()
        
        # Create story context
        story_context = StoryContext(
            story_id=uuid.UUID(story_id),
            current_chapter_id=uuid.UUID(chapter_id),
            story_metadata=story.dict(),
            generation_settings=story.generation_settings,
            image_settings=story.image_settings,
            characters=characters,
            world_elements=[],
            previous_content=chapter.content,
            continuation_context=chapter.continuation_context
        )
        
        # Start background continuation
        background_tasks.add_task(
            _execute_continuation_workflow,
            task_id,
            story_context,
            chapter_id,
            chapter.content,
            request.dict(),
            supabase
        )
        
        return GenerationResponse(
            task_id=task_id,
            status="processing",
            message="Chapter continuation started",
            estimated_completion_time=30
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start continuation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tasks/{task_id}")
async def get_task_status(
    task_id: str,
    current_user: Dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """Get task status and results"""
    try:
        result = supabase.table("generation_tasks")\
            .select("*")\
            .eq("id", task_id)\
            .eq("user_id", current_user["id"])\
            .execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Task not found")
        
        task = GenerationTask(**result.data[0])
        
        response = {
            "task_id": task_id,
            "status": task.status,
            "progress": task.progress,
            "created_at": task.created_at,
            "updated_at": task.updated_at,
            "completed_at": task.completed_at
        }
        
        if task.result:
            response["result"] = task.result
        
        if task.error_message:
            response["error"] = task.error_message
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get task status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== CHARACTER MANAGEMENT ROUTES =====

@router.post("/characters", response_model=Character)
async def create_character(
    character: CharacterCreate,
    current_user: Dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """Create a new character"""
    try:
        character_data = character.dict()
        character_data["user_id"] = current_user["id"]
        
        result = supabase.table("characters").insert(character_data).execute()
        
        if result.data:
            return Character(**result.data[0])
        else:
            raise HTTPException(status_code=400, detail="Failed to create character")
            
    except Exception as e:
        logger.error(f"Failed to create character: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/characters", response_model=List[Character])
async def get_user_characters(
    current_user: Dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Get user's characters"""
    try:
        result = supabase.table("characters")\
            .select("*")\
            .eq("user_id", current_user["id"])\
            .range(offset, offset + limit - 1)\
            .order("created_at", desc=True)\
            .execute()
        
        return [Character(**character) for character in result.data]
        
    except Exception as e:
        logger.error(f"Failed to get characters: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stories/{story_id}/characters/{character_id}")
async def add_character_to_story(
    story_id: str,
    character_id: str,
    role: str = "supporting",
    importance_score: int = 5,
    current_user: Dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """Add character to story"""
    try:
        # Verify story ownership
        story_result = supabase.table("stories")\
            .select("id")\
            .eq("id", story_id)\
            .eq("user_id", current_user["id"])\
            .execute()
        
        if not story_result.data:
            raise HTTPException(status_code=404, detail="Story not found")
        
        # Verify character ownership
        character_result = supabase.table("characters")\
            .select("id")\
            .eq("id", character_id)\
            .eq("user_id", current_user["id"])\
            .execute()
        
        if not character_result.data:
            raise HTTPException(status_code=404, detail="Character not found")
        
        # Add relationship
        relationship_data = {
            "story_id": story_id,
            "character_id": character_id,
            "role": role,
            "importance_score": importance_score
        }
        
        result = supabase.table("story_characters").insert(relationship_data).execute()
        
        if result.data:
            return {"message": "Character added to story successfully"}
        else:
            raise HTTPException(status_code=400, detail="Failed to add character to story")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to add character to story: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== IMAGE GENERATION ROUTES =====

@router.post("/stories/{story_id}/generate-image", response_model=ImageGenerationResult)
async def generate_story_image(
    story_id: str,
    request: ImageGenerationRequest,
    current_user: Dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """Generate image for story scene"""
    try:
        # Verify story ownership
        story_result = supabase.table("stories")\
            .select("*")\
            .eq("id", story_id)\
            .eq("user_id", current_user["id"])\
            .execute()
        
        if not story_result.data:
            raise HTTPException(status_code=404, detail="Story not found")
        
        story = Story(**story_result.data[0])
        
        # Check if images are enabled for this story
        if not story.image_settings.get("enabled", False):
            raise HTTPException(status_code=400, detail="Image generation not enabled for this story")
        
        # Get image service
        image_service = await get_image_service()
        
        # Generate image
        result = await image_service.analyze_scene(
            scene_description=request.content_context,
            characters_in_scene=[str(char_id) for char_id in request.characters_in_scene],
            setting=request.setting_description or "scene setting",
            mood=request.mood or "neutral",
            style=request.style_preferences.get("style", "realistic"),
            genre_style=story.genre
        )
        
        # Store visual asset
        asset_data = {
            "story_id": story_id,
            "chapter_id": request.chapter_id,
            "segment_id": request.segment_id,
            "asset_type": request.image_type.value,
            "image_url": result["image_url"],
            "generation_prompt": result.get("prompt_used", {}).get("prompt", ""),
            "image_metadata": result
        }
        
        supabase.table("visual_assets").insert(asset_data).execute()
        
        return ImageGenerationResult(
            image_url=result["image_url"],
            generation_prompt=result.get("prompt_used", {}).get("prompt", ""),
            image_metadata=result
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate image: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stories/{story_id}/generate-poster", response_model=PosterGenerationResult)
async def generate_story_poster(
    story_id: str,
    request: PosterGenerationRequest,
    current_user: Dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """Generate promotional poster for story"""
    try:
        # Verify story ownership
        story_result = supabase.table("stories")\
            .select("*")\
            .eq("id", story_id)\
            .eq("user_id", current_user["id"])\
            .execute()
        
        if not story_result.data:
            raise HTTPException(status_code=404, detail="Story not found")
        
        story = Story(**story_result.data[0])
        
        # Get image service
        image_service = await get_image_service()
        
        # Get story context for poster creation
        story_context = StoryContext(
            story_id=uuid.UUID(story_id),
            story_metadata=story.dict(),
            generation_settings=story.generation_settings,
            image_settings=story.image_settings,
            characters=[],
            world_elements=[],
            previous_content="",
            continuation_context={}
        )
        
        # Create agent context for visual storytelling agent
        agent_context = AgentContext(
            agent_type=AgentType.VISUAL_STORYTELLING,
            task_id=str(uuid.uuid4()),
            story_context=story_context,
            user_input="",
            agent_specific_data={
                "task_type": "generate_story_poster",
                "poster_type": request.poster_type.value,
                "story_title": story.title,
                "custom_elements": request.custom_elements
            }
        )
        
        # This would use the visual storytelling agent
        # For now, return a placeholder response
        poster_result = {
            "poster_variants": [
                {
                    "image_url": "https://placeholder.example.com/poster.jpg",
                    "generation_prompt": f"Poster for {story.title}",
                    "image_metadata": {"type": request.poster_type.value}
                }
            ],
            "design_rationale": f"Created {request.poster_type.value} style poster for {story.genre} story",
            "marketing_suggestions": [
                "Use on social media for promotion",
                "Consider for book cover design",
                "Adapt for different formats"
            ]
        }
        
        return PosterGenerationResult(**poster_result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate poster: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== SYSTEM STATUS ROUTES =====

@router.get("/health")
async def health_check():
    """System health check"""
    try:
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "services": {}
        }
        
        # Check vector service
        try:
            vector_service = await get_vector_service()
            vector_health = await vector_service.health_check()
            health_status["services"]["vector_service"] = vector_health
        except Exception as e:
            health_status["services"]["vector_service"] = {"status": "unhealthy", "error": str(e)}
        
        # Check LLM service
        try:
            llm_service = await get_llm_service()
            llm_health = await llm_service.health_check()
            health_status["services"]["llm_service"] = llm_health
        except Exception as e:
            health_status["services"]["llm_service"] = {"status": "unhealthy", "error": str(e)}
        
        # Check image service
        try:
            image_service = await get_image_service()
            image_health = await image_service.health_check()
            health_status["services"]["image_service"] = image_health
        except Exception as e:
            health_status["services"]["image_service"] = {"status": "unhealthy", "error": str(e)}
        
        # Determine overall status
        service_statuses = [service.get("status", "unhealthy") for service in health_status["services"].values()]
        if all(status == "healthy" for status in service_statuses):
            health_status["status"] = "healthy"
        elif any(status == "healthy" for status in service_statuses):
            health_status["status"] = "degraded"
        else:
            health_status["status"] = "unhealthy"
        
        return health_status
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@router.get("/stats")
async def get_system_stats(
    current_user: Dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """Get system statistics"""
    try:
        stats = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_stats": {},
            "service_stats": {}
        }
        
        # Get user stats
        user_id = current_user["id"]
        
        # Count user's stories
        stories_result = supabase.table("stories")\
            .select("id", count="exact")\
            .eq("user_id", user_id)\
            .execute()
        
        # Count user's characters
        characters_result = supabase.table("characters")\
            .select("id", count="exact")\
            .eq("user_id", user_id)\
            .execute()
        
        # Count user's generation tasks
        tasks_result = supabase.table("generation_tasks")\
            .select("id", count="exact")\
            .eq("user_id", user_id)\
            .execute()
        
        stats["user_stats"] = {
            "total_stories": stories_result.count,
            "total_characters": characters_result.count,
            "total_generations": tasks_result.count
        }
        
        # Get service stats
        try:
            vector_service = await get_vector_service()
            stats["service_stats"]["vector_service"] = await vector_service.get_collection_stats("context_embeddings")
        except:
            pass
        
        try:
            llm_service = await get_llm_service()
            stats["service_stats"]["llm_service"] = llm_service.get_provider_stats()
        except:
            pass
        
        try:
            image_service = await get_image_service()
            stats["service_stats"]["image_service"] = image_service.get_generation_stats()
        except:
            pass
        
        return stats
        
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== BACKGROUND TASK FUNCTIONS =====

async def _execute_generation_workflow(
    task_id: str,
    story_context: StoryContext,
    user_input: str,
    request_data: Dict[str, Any],
    supabase
):
    """Execute story generation workflow in background"""
    try:
        # Update task status
        supabase.table("generation_tasks")\
            .update({"status": "processing", "progress": 10})\
            .eq("id", task_id)\
            .execute()
        
        # Execute workflow
        result = await execute_story_generation(
            task_id=task_id,
            story_context=story_context,
            user_input=user_input,
            generation_mode=request_data.get("generation_mode", "ai_guided"),
            target_word_count=request_data.get("target_word_count", 250),
            include_images=story_context.image_settings.get("enabled", False)
        )
        
        # Update task with result
        update_data = {
            "status": "completed" if result.get("success") else "failed",
            "progress": 100,
            "result": result,
            "completed_at": datetime.utcnow().isoformat()
        }
        
        if not result.get("success"):
            update_data["error_message"] = result.get("error", "Generation failed")
        
        supabase.table("generation_tasks")\
            .update(update_data)\
            .eq("id", task_id)\
            .execute()
        
        logger.info(f"Generation workflow completed for task {task_id}")
        
    except Exception as e:
        logger.error(f"Generation workflow failed for task {task_id}: {e}")
        
        # Update task with error
        supabase.table("generation_tasks")\
            .update({
                "status": "failed",
                "progress": 0,
                "error_message": str(e),
                "completed_at": datetime.utcnow().isoformat()
            })\
            .eq("id", task_id)\
            .execute()

async def _execute_continuation_workflow(
    task_id: str,
    story_context: StoryContext,
    chapter_id: str,
    previous_content: str,
    request_data: Dict[str, Any],
    supabase
):
    """Execute chapter continuation workflow in background"""
    try:
        # Update task status
        supabase.table("generation_tasks")\
            .update({"status": "processing", "progress": 20})\
            .eq("id", task_id)\
            .execute()
        
        # Execute workflow
        result = await execute_chapter_continuation(
            task_id=task_id,
            story_context=story_context,
            chapter_id=chapter_id,
            previous_content=previous_content,
            user_direction=request_data.get("user_input"),
            continuation_mode=request_data.get("generation_mode", "seamless"),
            target_segments=request_data.get("target_word_count", 250) // 50  # Rough segment calculation
        )
        
        # Update task with result
        update_data = {
            "status": "completed" if result.get("success") else "failed",
            "progress": 100,
            "result": result,
            "completed_at": datetime.utcnow().isoformat()
        }
        
        if not result.get("success"):
            update_data["error_message"] = result.get("error", "Continuation failed")
        
        supabase.table("generation_tasks")\
            .update(update_data)\
            .eq("id", task_id)\
            .execute()
        
        logger.info(f"Continuation workflow completed for task {task_id}")
        
    except Exception as e:
        logger.error(f"Continuation workflow failed for task {task_id}: {e}")
        
        # Update task with error
        supabase.table("generation_tasks")\
            .update({
                "status": "failed",
                "progress": 0,
                "error_message": str(e),
                "completed_at": datetime.utcnow().isoformat()
            })\
            .eq("id", task_id)\
            .execute()
