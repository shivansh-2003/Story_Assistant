# models/story_models.py
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum
import uuid

class StoryStatus(str, Enum):
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    PUBLISHED = "published"
    ARCHIVED = "archived"

class GenerationMode(str, Enum):
    AI_GUIDED = "ai_guided"
    COLLABORATIVE = "collaborative"
    USER_INPUT = "user_input"
    HYBRID = "hybrid"

class Genre(str, Enum):
    FANTASY = "fantasy"
    SCIENCE_FICTION = "science_fiction"
    MYSTERY = "mystery"
    ROMANCE = "romance"
    THRILLER = "thriller"
    HORROR = "horror"
    HISTORICAL_FICTION = "historical_fiction"
    CONTEMPORARY = "contemporary"
    YOUNG_ADULT = "young_adult"
    CHILDREN = "children"

class TargetAudience(str, Enum):
    CHILDREN = "children"
    YOUNG_ADULT = "young_adult"
    ADULT = "adult"
    ALL_AGES = "all_ages"

class WritingStyle(str, Enum):
    DESCRIPTIVE = "descriptive"
    DIALOGUE_HEAVY = "dialogue_heavy"
    ACTION_PACKED = "action_packed"
    INTROSPECTIVE = "introspective"
    HUMOROUS = "humorous"
    DARK = "dark"
    POETIC = "poetic"

# Base models
class BaseStoryModel(BaseModel):
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            uuid.UUID: lambda v: str(v)
        }

# Story Settings Models
class GenerationSettings(BaseModel):
    words_per_segment: int = Field(default=250, ge=50, le=2000)
    generation_style: WritingStyle = WritingStyle.DESCRIPTIVE
    auto_continue_limit: Optional[int] = Field(default=None, ge=1, le=20)
    pause_for_input_frequency: int = Field(default=3, ge=1, le=10)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=2000, ge=100, le=4000)
    primary_llm: str = Field(default="openai")


class ImageSettings(BaseModel):
    enabled: bool = True
    frequency: str = Field(default="key_scenes_only") # every_segment, key_scenes_only, chapter_end_only
    style_consistency: str = Field(default="moderate") # strict, moderate, flexible
    character_focus: str = Field(default="scene_dependent") # always_include, scene_dependent, minimal
    image_style: str = Field(default="realistic") # realistic, anime, artistic, sketch
    resolution: str = Field(default="1024x1024")

class StoryMetadata(BaseModel):
    themes: List[str] = []
    setting_time_period: Optional[str] = None
    setting_location: Optional[str] = None
    content_warnings: List[str] = []
    inspiration_sources: List[str] = []
    tags: List[str] = []
    estimated_length: Optional[str] = None # short, medium, long, epic

# Story Models
class StoryBase(BaseStoryModel):
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = Field(None, max_length=2000)
    genre: Genre
    target_audience: TargetAudience = TargetAudience.ADULT
    writing_style: WritingStyle = WritingStyle.DESCRIPTIVE
    story_metadata: StoryMetadata = Field(default_factory=StoryMetadata)
    generation_settings: GenerationSettings = Field(default_factory=GenerationSettings)
    image_settings: ImageSettings = Field(default_factory=ImageSettings)

class StoryCreate(StoryBase):
    pass

class StoryUpdate(BaseStoryModel):
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = Field(None, max_length=2000)
    genre: Optional[Genre] = None
    target_audience: Optional[TargetAudience] = None
    writing_style: Optional[WritingStyle] = None
    story_metadata: Optional[StoryMetadata] = None
    generation_settings: Optional[GenerationSettings] = None
    image_settings: Optional[ImageSettings] = None
    status: Optional[StoryStatus] = None

class Story(StoryBase):
    id: uuid.UUID
    user_id: uuid.UUID
    status: StoryStatus = StoryStatus.DRAFT
    total_word_count: int = 0
    total_chapters: int = 0
    created_at: datetime
    updated_at: datetime

# Chapter Models
class ChapterBase(BaseStoryModel):
    title: Optional[str] = Field(None, max_length=500)
    content: str = ""
    chapter_order: int = Field(..., ge=1)
    chapter_summary: Optional[str] = Field(None, max_length=1000)
    generation_mode: GenerationMode = GenerationMode.AI_GUIDED

class ChapterCreate(ChapterBase):
    story_id: uuid.UUID

class ChapterUpdate(BaseStoryModel):
    title: Optional[str] = Field(None, max_length=500)
    content: Optional[str] = None
    chapter_summary: Optional[str] = Field(None, max_length=1000)
    generation_mode: Optional[GenerationMode] = None
    status: Optional[str] = None

class ContinuationContext(BaseModel):
    previous_chapter_ending: Dict[str, Any] = {}
    character_states: Dict[str, Any] = {}
    relationship_changes: Dict[str, Any] = {}
    plot_threads: Dict[str, Any] = {}
    world_state_changes: Dict[str, Any] = {}
    next_chapter_setup: Dict[str, Any] = {}

class Chapter(ChapterBase):
    id: uuid.UUID
    story_id: uuid.UUID
    word_count: int = 0
    segment_count: int = 0
    chapter_metadata: Dict[str, Any] = {}
    continuation_context: ContinuationContext = Field(default_factory=ContinuationContext)
    status: str = "draft"
    created_at: datetime
    updated_at: datetime

# Chapter Segment Models
class ChapterSegmentBase(BaseStoryModel):
    content: str = Field(..., min_length=1)
    segment_order: int = Field(..., ge=1)
    generation_mode: GenerationMode = GenerationMode.AI_GUIDED
    user_input: Optional[str] = None

class ChapterSegmentCreate(ChapterSegmentBase):
    chapter_id: uuid.UUID

class ChapterSegment(ChapterSegmentBase):
    id: uuid.UUID
    chapter_id: uuid.UUID
    word_count: int = 0
    generation_metadata: Dict[str, Any] = {}
    created_at: datetime

# Generation Request Models
class ContentGenerationRequest(BaseModel):
    story_id: uuid.UUID
    chapter_id: Optional[uuid.UUID] = None
    user_input: Optional[str] = None
    generation_mode: GenerationMode = GenerationMode.AI_GUIDED
    generation_settings: Optional[GenerationSettings] = None
    continue_from_last: bool = True
    target_word_count: Optional[int] = Field(None, ge=50, le=5000)

class ChapterGenerationRequest(BaseModel):
    story_id: uuid.UUID
    chapter_title: Optional[str] = None
    user_direction: Optional[str] = None
    generation_settings: Optional[GenerationSettings] = None

class SegmentGenerationRequest(BaseModel):
    chapter_id: uuid.UUID
    user_input: Optional[str] = None
    generation_mode: GenerationMode = GenerationMode.AI_GUIDED
    target_word_count: int = Field(default=250, ge=50, le=2000)

# Response Models
class GenerationResponse(BaseModel):
    task_id: str
    status: str
    message: str
    estimated_completion_time: Optional[int] = None # seconds

class GenerationResult(BaseModel):
    content: str
    word_count: int
    generation_metadata: Dict[str, Any] = {}
    quality_score: Optional[float] = None
    suggestions: List[str] = []

class StoryWithChapters(Story):
    chapters: List[Chapter] = []

class ChapterWithSegments(Chapter):
    segments: List[ChapterSegment] = []

# Validation
class StoryBase(BaseStoryModel):
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = Field(None, max_length=2000)
    genre: Genre
    target_audience: TargetAudience = TargetAudience.ADULT
    writing_style: WritingStyle = WritingStyle.DESCRIPTIVE
    story_metadata: StoryMetadata = Field(default_factory=StoryMetadata)
    generation_settings: GenerationSettings = Field(default_factory=GenerationSettings)
    image_settings: ImageSettings = Field(default_factory=ImageSettings)
    
    @validator('title')
    def title_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip()
    
    @validator('description')
    def description_validation(cls, v):
        if v is not None:
            return v.strip() if v.strip() else None
        return v
