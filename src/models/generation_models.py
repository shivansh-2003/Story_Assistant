# models/generation_models.py
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum
import uuid

class TaskStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class AgentType(str, Enum):
    CREATIVE_DIRECTOR = "creative_director"
    NARRATIVE_INTELLIGENCE = "narrative_intelligence"
    QUALITY_ASSURANCE = "quality_assurance"
    WORLD_BUILDING = "world_building"
    VISUAL_STORYTELLING = "visual_storytelling"
    CONTINUATION_CONTEXT = "continuation_context"

class GenerationType(str, Enum):
    CHAPTER = "chapter"
    SEGMENT = "segment"
    CHARACTER = "character"
    WORLD_ELEMENT = "world_element"
    IMAGE = "image"
    POSTER = "poster"
    CONTINUATION = "continuation"

class ImageType(str, Enum):
    SCENE_IMAGE = "scene_image"
    CHARACTER_PORTRAIT = "character_portrait"
    SETTING_IMAGE = "setting_image"
    POSTER = "poster"
    COVER_ART = "cover_art"

class PosterType(str, Enum):
    CHARACTER_FOCUSED = "character_focused"
    ATMOSPHERIC = "atmospheric"
    ACTION_ORIENTED = "action_oriented"
    MINIMALIST = "minimalist"
    CLASSIC_BOOK_COVER = "classic_book_cover"

# Base Generation Models
class BaseGenerationModel(BaseModel):
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            uuid.UUID: lambda v: str(v)
        }

# Context Models
class StoryContext(BaseModel):
    story_id: uuid.UUID
    current_chapter_id: Optional[uuid.UUID] = None
    story_metadata: Dict[str, Any] = {}
    generation_settings: Dict[str, Any] = {}
    image_settings: Dict[str, Any] = {}
    characters: List[Dict[str, Any]] = []
    world_elements: List[Dict[str, Any]] = []
    previous_content: Optional[str] = None
    continuation_context: Dict[str, Any] = {}

class AgentContext(BaseModel):
    agent_type: AgentType
    task_id: str
    story_context: StoryContext
    user_input: Optional[str] = None
    agent_specific_data: Dict[str, Any] = {}
    previous_agent_results: List[Dict[str, Any]] = []

# Task Models
class GenerationTaskBase(BaseGenerationModel):
    task_type: GenerationType
    task_data: Dict[str, Any]
    priority: int = Field(default=5, ge=1, le=10)

class GenerationTaskCreate(GenerationTaskBase):
    user_id: uuid.UUID

class GenerationTaskUpdate(BaseGenerationModel):
    status: Optional[TaskStatus] = None
    progress: Optional[int] = Field(None, ge=0, le=100)
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

class GenerationTask(GenerationTaskBase):
    id: uuid.UUID
    user_id: uuid.UUID
    status: TaskStatus = TaskStatus.PENDING
    progress: int = Field(default=0, ge=0, le=100)
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None

# Agent Communication Models
class AgentMessage(BaseModel):
    agent_id: str
    task_type: str
    payload: Dict[str, Any]
    context: StoryContext
    priority: int = Field(default=5, ge=1, le=10)
    dependencies: List[str] = []
    correlation_id: str

class AgentResponse(BaseModel):
    agent_id: str
    task_id: str
    success: bool
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time_ms: Optional[int] = None
    next_agents: List[str] = []

# Content Generation Models
class ContentGenerationContext(BaseModel):
    target_word_count: int = Field(default=250, ge=50, le=5000)
    tone: Optional[str] = None
    perspective: Optional[str] = None  # first_person, third_person_limited, etc.
    focus_characters: List[uuid.UUID] = []
    scene_setting: Optional[str] = None
    emotional_tone: Optional[str] = None
    plot_advancement: Optional[str] = None

class ContentGenerationRequest(BaseGenerationModel):
    story_id: uuid.UUID
    chapter_id: Optional[uuid.UUID] = None
    user_input: Optional[str] = None
    generation_context: ContentGenerationContext = Field(default_factory=ContentGenerationContext)
    agents_to_use: List[AgentType] = Field(default_factory=lambda: [
        AgentType.CREATIVE_DIRECTOR,
        AgentType.NARRATIVE_INTELLIGENCE,
        AgentType.QUALITY_ASSURANCE
    ])
    include_images: bool = False
    continuation_mode: bool = True

class ContentGenerationResult(BaseModel):
    content: str
    word_count: int
    quality_metrics: Dict[str, float] = {}
    character_consistency_scores: Dict[str, float] = {}
    generated_images: List[str] = []
    generation_metadata: Dict[str, Any] = {}
    agent_contributions: Dict[str, str] = {}

# Image Generation Models
class ImageGenerationRequest(BaseModel):
    story_id: uuid.UUID
    chapter_id: Optional[uuid.UUID] = None
    segment_id: Optional[uuid.UUID] = None
    image_type: ImageType
    content_context: str = Field(..., min_length=10, max_length=2000)
    characters_in_scene: List[uuid.UUID] = []
    setting_description: Optional[str] = None
    mood: Optional[str] = None
    style_preferences: Dict[str, Any] = {}

class ImageGenerationResult(BaseModel):
    image_url: str
    generation_prompt: str
    image_metadata: Dict[str, Any] = {}
    character_accuracy_score: Optional[float] = None

# Poster Generation Models
class PosterGenerationRequest(BaseModel):
    story_id: uuid.UUID
    poster_type: PosterType = PosterType.CHARACTER_FOCUSED
    title_override: Optional[str] = None
    include_characters: List[uuid.UUID] = []
    color_palette: Optional[List[str]] = None
    style_reference: Optional[str] = None
    tagline: Optional[str] = None
    custom_elements: Dict[str, Any] = {}

class PosterGenerationResult(BaseModel):
    poster_variants: List[ImageGenerationResult]
    design_rationale: str
    marketing_suggestions: List[str] = []

# Quality Assessment Models
class QualityMetrics(BaseModel):
    grammar_score: float = Field(..., ge=0.0, le=1.0)
    readability_score: float = Field(..., ge=0.0, le=1.0)
    character_consistency_score: float = Field(..., ge=0.0, le=1.0)
    plot_coherence_score: float = Field(..., ge=0.0, le=1.0)
    genre_adherence_score: float = Field(..., ge=0.0, le=1.0)
    overall_quality_score: float = Field(..., ge=0.0, le=1.0)

class QualityAssessmentResult(BaseModel):
    quality_metrics: QualityMetrics
    identified_issues: List[str] = []
    improvement_suggestions: List[str] = []
    auto_corrections: Dict[str, str] = {}
    requires_human_review: bool = False

# World Building Models
class WorldElementType(str, Enum):
    LOCATION = "location"
    CULTURE = "culture"
    TECHNOLOGY = "technology"
    MAGIC_SYSTEM = "magic_system"
    POLITICAL_SYSTEM = "political_system"
    ECONOMY = "economy"
    RELIGION = "religion"
    LANGUAGE = "language"
    HISTORY = "history"
    NATURAL_LAW = "natural_law"

class WorldElementRequest(BaseModel):
    story_id: uuid.UUID
    element_type: WorldElementType
    name: str = Field(..., min_length=1, max_length=255)
    description_prompt: str = Field(..., min_length=10, max_length=1000)
    related_elements: List[uuid.UUID] = []
    consistency_requirements: List[str] = []

class WorldElementResult(BaseModel):
    element_id: uuid.UUID
    name: str
    description: str
    properties: Dict[str, Any] = {}
    relationships: Dict[str, Any] = {}
    consistency_notes: List[str] = []

# Continuation Context Models
class CharacterState(BaseModel):
    character_id: uuid.UUID
    emotional_state: str
    physical_location: str
    current_goal: str
    unresolved_tensions: List[str] = []
    recent_interactions: List[str] = []

class RelationshipChange(BaseModel):
    relationship_id: uuid.UUID
    status_change: str  # improved, deteriorated, complicated
    recent_interaction: str
    unresolved_issues: List[str] = []

class PlotThread(BaseModel):
    thread_id: str
    description: str
    status: str  # active, resolved, dormant
    importance: int = Field(..., ge=1, le=10)
    related_characters: List[uuid.UUID] = []

class ContinuationContextData(BaseModel):
    chapter_ending_summary: str
    character_states: Dict[str, CharacterState] = {}
    relationship_changes: Dict[str, RelationshipChange] = {}
    plot_threads: Dict[str, PlotThread] = {}
    world_state_changes: Dict[str, Any] = {}
    emotional_momentum: str
    suggested_next_scenes: List[str] = []

# Workflow Models
class WorkflowStep(BaseModel):
    step_id: str
    agent_type: AgentType
    dependencies: List[str] = []
    input_requirements: List[str] = []
    output_keys: List[str] = []
    timeout_seconds: int = 300

class WorkflowDefinition(BaseModel):
    workflow_id: str
    name: str
    description: str
    steps: List[WorkflowStep]
    parallel_execution: bool = False
    retry_policy: Dict[str, Any] = {}

class WorkflowExecution(BaseModel):
    execution_id: str
    workflow_id: str
    task_id: str
    status: TaskStatus = TaskStatus.PENDING
    current_step: Optional[str] = None
    step_results: Dict[str, Any] = {}
    started_at: datetime
    completed_at: Optional[datetime] = None
    error_details: Optional[str] = None

# Analytics and Learning Models
class GenerationAnalytics(BaseModel):
    user_id: uuid.UUID
    story_id: uuid.UUID
    generation_type: GenerationType
    agent_performances: Dict[str, Dict[str, float]] = {}
    user_satisfaction_score: Optional[float] = Field(None, ge=1.0, le=5.0)
    generation_time_ms: int
    token_count: int
    cost_estimate: Optional[float] = None
    improvement_areas: List[str] = []

class UserPreference(BaseModel):
    user_id: uuid.UUID
    preference_type: str
    preference_data: Dict[str, Any] = {}
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    last_updated: datetime

# Feedback Models
class UserFeedback(BaseModel):
    generation_id: uuid.UUID
    user_id: uuid.UUID
    rating: int = Field(..., ge=1, le=5)
    feedback_text: Optional[str] = Field(None, max_length=2000)
    specific_issues: List[str] = []
    suggestions: Optional[str] = Field(None, max_length=1000)
    would_use_again: bool = True

class FeedbackAnalysis(BaseModel):
    feedback_id: uuid.UUID
    sentiment_score: float = Field(..., ge=-1.0, le=1.0)
    key_themes: List[str] = []
    actionable_insights: List[str] = []
    priority_level: int = Field(..., ge=1, le=5)

# Validation Functions
@validator('progress')
def validate_progress(cls, v):
    if v is not None and (v < 0 or v > 100):
        raise ValueError('Progress must be between 0 and 100')
    return v

@validator('priority')
def validate_priority(cls, v):
    if v < 1 or v > 10:
        raise ValueError('Priority must be between 1 and 10')
    return v

# Apply validators to relevant models
GenerationTask.__validators__['validate_progress'] = validate_progress
GenerationTaskBase.__validators__['validate_priority'] = validate_priority
AgentMessage.__validators__['validate_priority'] = validate_priority
