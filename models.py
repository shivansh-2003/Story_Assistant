from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

__all__ = [
    "PersonalityType", "SpeakingStyle", "StoryTheme", "Character", 
    "StorySegment", "Story", "StoryGenerationRequest", "StoryEditRequest",
    "StoryResponse", "EditResponse", "AudioRequest", "PDFRequest", "StoryCreationRequest"
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

class Character(BaseModel):
    name: str = Field(..., description="Character name")
    age: Optional[int] = Field(None, description="Character age")
    occupation: Optional[str] = Field(None, description="Character occupation")
    primary_trait: PersonalityType = Field(..., description="Primary personality trait")
    secondary_trait: Optional[PersonalityType] = Field(None, description="Secondary trait")
    fatal_flaw: Optional[str] = Field(None, description="Character weakness")
    motivation: Optional[str] = Field(None, description="Core goal/motivation")
    appearance: str = Field(..., description="Physical description")
    speaking_style: Optional[SpeakingStyle] = Field(None, description="How they speak")
    backstory: Optional[str] = Field(None, description="Character background")
    relationships: Optional[Dict[str, str]] = Field(default_factory=dict, description="Relationships with other characters")
    special_abilities: Optional[List[str]] = Field(default_factory=list, description="Special skills/abilities")

class StorySegment(BaseModel):
    id: str = Field(..., description="Unique segment ID")
    content: str = Field(..., description="Story content")
    order: int = Field(..., description="Segment order in story")
    is_edited: bool = Field(default=False, description="Whether segment was edited")
    original_content: Optional[str] = Field(None, description="Original content before editing")

class Story(BaseModel):
    id: str = Field(..., description="Unique story ID")
    title: Optional[str] = Field(None, description="Story title")
    theme: StoryTheme = Field(..., description="Story theme")
    characters: List[Character] = Field(default_factory=list, description="Story characters")
    segments: List[StorySegment] = Field(default_factory=list, description="Story segments")
    base_idea: str = Field(..., description="Initial story idea")
    is_completed: bool = Field(default=False, description="Whether story is finished")

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