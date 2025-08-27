# models/character_models.py
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import uuid

class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    NON_BINARY = "non_binary"
    OTHER = "other"
    UNSPECIFIED = "unspecified"

class CharacterRole(str, Enum):
    PROTAGONIST = "protagonist"
    ANTAGONIST = "antagonist"
    DEUTERAGONIST = "deuteragonist"  # Second most important character
    SUPPORTING = "supporting"
    MINOR = "minor"
    BACKGROUND = "background"

class RelationshipType(str, Enum):
    FAMILY = "family"
    ROMANTIC = "romantic"
    FRIEND = "friend"
    ENEMY = "enemy"
    ALLY = "ally"
    RIVAL = "rival"
    MENTOR = "mentor"
    STUDENT = "student"
    COLLEAGUE = "colleague"
    STRANGER = "stranger"
    COMPLICATED = "complicated"

class CharacterStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DECEASED = "deceased"
    MISSING = "missing"
    RETIRED = "retired"

# Base Character Models
class BaseCharacterModel(BaseModel):
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            uuid.UUID: lambda v: str(v)
        }

# Character Attributes
class PhysicalAttributes(BaseModel):
    height: Optional[str] = None
    weight: Optional[str] = None
    build: Optional[str] = None  # slim, athletic, stocky, etc.
    hair_color: Optional[str] = None
    hair_style: Optional[str] = None
    eye_color: Optional[str] = None
    skin_tone: Optional[str] = None
    distinguishing_features: List[str] = []  # scars, tattoos, etc.
    clothing_style: Optional[str] = None
    voice_description: Optional[str] = None

class PersonalityTraits(BaseModel):
    core_traits: List[str] = []  # brave, intelligent, stubborn, etc.
    strengths: List[str] = []
    weaknesses: List[str] = []
    quirks: List[str] = []
    speech_patterns: List[str] = []  # formal, uses slang, stutters, etc.
    mannerisms: List[str] = []  # nervous habits, gestures, etc.

class CharacterBackground(BaseModel):
    birthplace: Optional[str] = None
    family_background: Optional[str] = None
    education: Optional[str] = None
    significant_events: List[str] = []
    formative_experiences: List[str] = []
    secrets: List[str] = []
    trauma: Optional[str] = None

class CharacterGoals(BaseModel):
    primary_goal: Optional[str] = None
    secondary_goals: List[str] = []
    internal_conflict: Optional[str] = None
    external_conflict: Optional[str] = None
    character_arc_direction: Optional[str] = None  # growth, fall, flat, etc.

class CharacterMetadata(BaseModel):
    inspiration: Optional[str] = None  # Real person, fictional character, etc.
    archetype: Optional[str] = None  # Hero, mentor, trickster, etc.
    symbolic_meaning: Optional[str] = None
    thematic_purpose: Optional[str] = None
    first_appearance_planned: Optional[str] = None
    character_development_notes: Optional[str] = None

# Main Character Models
class CharacterBase(BaseCharacterModel):
    name: str = Field(..., min_length=1, max_length=255)
    age: Optional[int] = Field(None, ge=0, le=1000)
    gender: Gender = Gender.UNSPECIFIED
    occupation: Optional[str] = Field(None, max_length=255)
    personality_traits: PersonalityTraits = Field(default_factory=PersonalityTraits)
    physical_description: Optional[str] = Field(None, max_length=2000)
    background_story: Optional[str] = Field(None, max_length=5000)
    goals: Optional[str] = Field(None, max_length=2000)
    fears: Optional[str] = Field(None, max_length=2000)
    character_metadata: CharacterMetadata = Field(default_factory=CharacterMetadata)

class CharacterCreate(CharacterBase):
    pass

class CharacterUpdate(BaseCharacterModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    age: Optional[int] = Field(None, ge=0, le=1000)
    gender: Optional[Gender] = None
    occupation: Optional[str] = Field(None, max_length=255)
    personality_traits: Optional[PersonalityTraits] = None
    physical_description: Optional[str] = Field(None, max_length=2000)
    background_story: Optional[str] = Field(None, max_length=5000)
    goals: Optional[str] = Field(None, max_length=2000)
    fears: Optional[str] = Field(None, max_length=2000)
    character_metadata: Optional[CharacterMetadata] = None

class Character(CharacterBase):
    id: uuid.UUID
    user_id: uuid.UUID
    embedding_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

# Story-Character Relationship Models
class StoryCharacterBase(BaseCharacterModel):
    story_id: uuid.UUID
    character_id: uuid.UUID
    role: CharacterRole
    importance_score: int = Field(default=5, ge=1, le=10)
    character_arc: Optional[str] = Field(None, max_length=2000)
    first_appearance_chapter: Optional[int] = Field(None, ge=1)
    status: CharacterStatus = CharacterStatus.ACTIVE

class StoryCharacterCreate(StoryCharacterBase):
    pass

class StoryCharacterUpdate(BaseCharacterModel):
    role: Optional[CharacterRole] = None
    importance_score: Optional[int] = Field(None, ge=1, le=10)
    character_arc: Optional[str] = Field(None, max_length=2000)
    first_appearance_chapter: Optional[int] = Field(None, ge=1)
    status: Optional[CharacterStatus] = None

class StoryCharacter(StoryCharacterBase):
    id: uuid.UUID

# Character Relationship Models
class CharacterRelationshipBase(BaseCharacterModel):
    character1_id: uuid.UUID
    character2_id: uuid.UUID
    relationship_type: RelationshipType
    strength: int = Field(default=5, ge=1, le=10)
    description: Optional[str] = Field(None, max_length=2000)
    status: str = Field(default="current")  # current, past, complicated
    relationship_metadata: Dict[str, Any] = {}

class CharacterRelationshipCreate(CharacterRelationshipBase):
    pass

class CharacterRelationshipUpdate(BaseCharacterModel):
    relationship_type: Optional[RelationshipType] = None
    strength: Optional[int] = Field(None, ge=1, le=10)
    description: Optional[str] = Field(None, max_length=2000)
    status: Optional[str] = None
    relationship_metadata: Optional[Dict[str, Any]] = None

class CharacterRelationship(CharacterRelationshipBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

# Extended Character with Relationships
class CharacterWithRelationships(Character):
    relationships: List[CharacterRelationship] = []
    story_roles: List[StoryCharacter] = []

# Character Consistency Models
class CharacterConsistencyCheck(BaseModel):
    character_id: uuid.UUID
    consistency_score: float = Field(..., ge=0.0, le=1.0)
    inconsistencies: List[str] = []
    suggestions: List[str] = []

class CharacterVoicePattern(BaseModel):
    character_id: uuid.UUID
    vocabulary_level: str  # simple, moderate, complex, formal
    sentence_structure: str  # short, varied, complex
    dialogue_style: str  # direct, rambling, poetic, technical
    common_phrases: List[str] = []
    topics_of_interest: List[str] = []
    speech_quirks: List[str] = []

# Character Generation Models
class CharacterGenerationRequest(BaseModel):
    story_id: uuid.UUID
    character_prompt: str = Field(..., min_length=10, max_length=1000)
    role: CharacterRole = CharacterRole.SUPPORTING
    detailed_generation: bool = True
    include_relationships: bool = True
    generate_backstory: bool = True

class CharacterGenerationResult(BaseModel):
    character: Character
    generation_notes: str
    suggested_relationships: List[Dict[str, Any]] = []
    character_arc_suggestions: List[str] = []

# Validators
@validator('name')
def name_must_not_be_empty(cls, v):
    if not v or not v.strip():
        raise ValueError('Character name cannot be empty')
    return v.strip()

@validator('physical_description', 'background_story', 'goals', 'fears')
def clean_text_fields(cls, v):
    if v is not None:
        return v.strip() if v.strip() else None
    return v

# Add validators to CharacterBase
CharacterBase.__validators__['name_must_not_be_empty'] = name_must_not_be_empty
CharacterBase.__validators__['clean_text_fields'] = clean_text_fields

# Character Analysis Models
class CharacterAnalysis(BaseModel):
    character_id: uuid.UUID
    personality_analysis: Dict[str, Any] = {}
    development_suggestions: List[str] = []
    relationship_opportunities: List[str] = []
    plot_potential: List[str] = []
    consistency_score: float = 0.0

class CharacterInteraction(BaseModel):
    characters: List[uuid.UUID]
    interaction_type: str  # dialogue, conflict, cooperation, etc.
    context: str
    emotional_dynamics: Dict[str, str] = {}
    relationship_changes: List[str] = []
