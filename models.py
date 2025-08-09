from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime

__all__ = [
    "PersonalityType", "SpeakingStyle", "StoryTheme", "ChapterStatus", "Character", 
    "Chapter", "Relationship", "StorySegment", "Story", "StoryGenerationRequest", 
    "StoryEditRequest", "StoryResponse", "EditResponse", "AudioRequest", "PDFRequest", 
    "StoryCreationRequest", "ChapterRequest", "ChapterResponse", "RelationshipRequest"
]

class PersonalityType(str, Enum):
    BRAVE = "brave"
    CLEVER = "clever"
    SHY = "shy"
    AGGRESSIVE = "aggressive"
    WISE = "wise"
    COMPASSIONATE = "compassionate"
    CUNNING = "cunning"

class SpeakingStyle(str, Enum):
    FORMAL = "formal"
    CASUAL = "casual"
    WITTY = "witty"
    SERIOUS = "serious"
    PLAYFUL = "playful"

class StoryTheme(str, Enum):
    FANTASY = "fantasy"
    MYSTERY = "mystery"
    ADVENTURE = "adventure"
    SCIFI = "sci-fi"
    HORROR = "horror"
    ROMANCE = "romance"

class ChapterStatus(str, Enum):
    DRAFT = "draft"
    IN_PROGRESS = "in-progress"
    COMPLETED = "completed"

class Character(BaseModel):
    id: Optional[str] = Field(None, description="Character ID")
    name: str = Field(..., description="Character name")
    age: Optional[int] = Field(None, description="Character age")
    occupation: Optional[str] = Field(None, description="Character occupation")
    role: Optional[str] = Field(None, description="Character role in story")
    primary_trait: PersonalityType = Field(..., description="Primary personality trait")
    secondary_trait: Optional[PersonalityType] = Field(None, description="Secondary trait")
    fatal_flaw: Optional[str] = Field(None, description="Character weakness")
    motivation: Optional[str] = Field(None, description="Core goal/motivation")
    appearance: str = Field(..., description="Physical description")
    personality: Optional[str] = Field(None, description="Detailed personality description")
    background: Optional[str] = Field(None, description="Character background/history")
    archetype: Optional[str] = Field(None, description="Character archetype")
    speaking_style: Optional[SpeakingStyle] = Field(None, description="How they speak")
    backstory: Optional[str] = Field(None, description="Character background")
    relationships: Optional[List[str]] = Field(default_factory=list, description="Character relationships")
    special_abilities: Optional[List[str]] = Field(default_factory=list, description="Special skills/abilities")

class Chapter(BaseModel):
    id: Optional[str] = Field(None, description="Chapter ID")
    title: str = Field(..., description="Chapter title")
    content: str = Field(default="", description="Chapter content")
    word_count: int = Field(default=0, description="Word count")
    status: ChapterStatus = Field(default=ChapterStatus.DRAFT, description="Chapter status")
    order: int = Field(..., description="Chapter order in story")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

class Relationship(BaseModel):
    id: Optional[str] = Field(None, description="Relationship ID")
    character1_id: str = Field(..., description="First character ID")
    character2_id: str = Field(..., description="Second character ID")
    type: str = Field(..., description="Relationship type (e.g., friend, enemy, mentor)")
    description: Optional[str] = Field(None, description="Relationship description")
    strength: Optional[int] = Field(None, description="Relationship strength (1-10)")

class StorySegment(BaseModel):
    id: str = Field(..., description="Unique segment ID")
    content: str = Field(..., description="Story content")
    order: int = Field(..., description="Segment order in story")
    is_edited: bool = Field(default=False, description="Whether segment was edited")
    original_content: Optional[str] = Field(None, description="Original content before editing")

class Story(BaseModel):
    id: str = Field(..., description="Unique story ID")
    title: Optional[str] = Field(None, description="Story title")
    genre: Optional[str] = Field(None, description="Story genre")
    description: Optional[str] = Field(None, description="Story description")
    premise: Optional[str] = Field(None, description="Story premise")
    setting: Optional[str] = Field(None, description="Story setting")
    target_audience: Optional[str] = Field(None, description="Target audience")
    theme: StoryTheme = Field(..., description="Story theme")
    characters: List[Character] = Field(default_factory=list, description="Story characters")
    chapters: List[Chapter] = Field(default_factory=list, description="Story chapters")
    segments: List[StorySegment] = Field(default_factory=list, description="Story segments")
    base_idea: str = Field(..., description="Initial story idea")
    is_completed: bool = Field(default=False, description="Whether story is finished")
    is_draft: bool = Field(default=True, description="Whether story is a draft")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

class StoryCreationRequest(BaseModel):
    base_idea: str = Field(..., description="Initial story idea")
    theme: StoryTheme = Field(..., description="Story theme")
    characters: Optional[List[Character]] = Field(default_factory=list, description="Story characters")

class StoryGenerationRequest(BaseModel):
    story_id: str
    user_choice: Optional[str] = Field(None, description="User's choice/input")
    auto_continue: bool = Field(default=False, description="Whether to auto-continue")
    characters: List[Character] = Field(default_factory=list)
    theme: StoryTheme
    previous_content: str = Field(..., description="Previous story content")

class StoryEditRequest(BaseModel):
    story_id: str
    segment_id: str
    edit_instruction: str = Field(..., description="How to edit the segment")
    original_content: str = Field(..., description="Content to be edited")
    context: Optional[str] = Field(None, description="Surrounding story context")
    characters: List[Character] = Field(default_factory=list)

class StoryResponse(BaseModel):
    success: bool
    story: Optional[Story] = None
    new_segment: Optional[StorySegment] = None
    message: str

class EditResponse(BaseModel):
    success: bool
    original_content: str
    edited_content: str
    segment_id: str
    message: str

class AudioRequest(BaseModel):
    story_id: str
    language: str = Field(default="en", description="Language code")
    
class PDFRequest(BaseModel):
    story_id: str

# Chapter management models
class ChapterRequest(BaseModel):
    title: str = Field(..., description="Chapter title")
    content: Optional[str] = Field("", description="Chapter content")
    status: Optional[ChapterStatus] = Field(ChapterStatus.DRAFT, description="Chapter status")

class ChapterResponse(BaseModel):
    success: bool
    chapter: Optional[Chapter] = None
    message: str

# Relationship management models
class RelationshipRequest(BaseModel):
    character1_id: str = Field(..., description="First character ID")
    character2_id: str = Field(..., description="Second character ID")
    type: str = Field(..., description="Relationship type")
    description: Optional[str] = Field(None, description="Relationship description")
    strength: Optional[int] = Field(None, description="Relationship strength (1-10)")

# Enhanced story request
class StoryUpdateRequest(BaseModel):
    title: Optional[str] = Field(None, description="Story title")
    genre: Optional[str] = Field(None, description="Story genre")
    description: Optional[str] = Field(None, description="Story description")
    premise: Optional[str] = Field(None, description="Story premise")
    setting: Optional[str] = Field(None, description="Story setting")
    target_audience: Optional[str] = Field(None, description="Target audience")
    theme: Optional[StoryTheme] = Field(None, description="Story theme")
    is_draft: Optional[bool] = Field(None, description="Whether story is a draft")