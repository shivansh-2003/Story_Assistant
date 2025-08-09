import uuid
from typing import Dict, List, Optional
from models import Story, StorySegment, Character, StoryTheme, Chapter, ChapterStatus, Relationship
from datetime import datetime
import json

class StoryManager:
    def __init__(self):
        self.stories: Dict[str, Story] = {}
        self.characters: Dict[str, Character] = {}
        self.relationships: Dict[str, Relationship] = {}
        
    def create_story(self, base_idea: str, theme: StoryTheme, characters: List[Character] = None) -> Story:
        """Create a new story"""
        story_id = str(uuid.uuid4())
        now = datetime.now()
        story = Story(
            id=story_id,
            theme=theme,
            base_idea=base_idea,
            characters=characters or [],
            chapters=[],
            segments=[],
            is_completed=False,
            is_draft=True,
            created_at=now,
            updated_at=now
        )
        self.stories[story_id] = story
        return story
    
    def get_story(self, story_id: str) -> Optional[Story]:
        """Get story by ID"""
        return self.stories.get(story_id)
    
    def add_segment(self, story_id: str, content: str) -> Optional[StorySegment]:
        """Add new segment to story"""
        story = self.get_story(story_id)
        if not story:
            return None
            
        segment_id = str(uuid.uuid4())
        segment = StorySegment(
            id=segment_id,
            content=content,
            order=len(story.segments) + 1
        )
        story.segments.append(segment)
        return segment
    
    def edit_segment(self, story_id: str, segment_id: str, new_content: str) -> bool:
        """Edit existing segment"""
        story = self.get_story(story_id)
        if not story:
            return False
            
        for segment in story.segments:
            if segment.id == segment_id:
                if not segment.is_edited:
                    segment.original_content = segment.content
                segment.content = new_content
                segment.is_edited = True
                return True
        return False
    
    def get_segment(self, story_id: str, segment_id: str) -> Optional[StorySegment]:
        """Get specific segment"""
        story = self.get_story(story_id)
        if not story:
            return None
            
        for segment in story.segments:
            if segment.id == segment_id:
                return segment
        return None
    
    def get_full_story_text(self, story_id: str) -> str:
        """Get complete story text"""
        story = self.get_story(story_id)
        if not story:
            return ""
            
        segments_text = [segment.content for segment in sorted(story.segments, key=lambda x: x.order)]
        return " ".join(segments_text)
    
    def complete_story(self, story_id: str) -> bool:
        """Mark story as completed"""
        story = self.get_story(story_id)
        if story:
            story.is_completed = True
            return True
        return False
    
    def add_character(self, story_id: str, character: Character) -> bool:
        """Add character to story"""
        story = self.get_story(story_id)
        if story and len(story.characters) < 10:
            story.characters.append(character)
            return True
        return False
    
    def get_context_for_segment(self, story_id: str, segment_id: str, context_range: int = 2) -> str:
        """Get surrounding context for a segment"""
        story = self.get_story(story_id)
        if not story:
            return ""
            
        target_segment = None
        target_order = 0
        
        for segment in story.segments:
            if segment.id == segment_id:
                target_segment = segment
                target_order = segment.order
                break
                
        if not target_segment:
            return ""
            
        # Get surrounding segments
        context_segments = []
        for segment in story.segments:
            if abs(segment.order - target_order) <= context_range and segment.id != segment_id:
                context_segments.append(segment)
                
        context_segments.sort(key=lambda x: x.order)
        return " ".join([seg.content for seg in context_segments])
    
    # Story Management Methods
    def update_story(self, story_id: str, **kwargs) -> bool:
        """Update story details"""
        story = self.get_story(story_id)
        if not story:
            return False
        
        for key, value in kwargs.items():
            if hasattr(story, key) and value is not None:
                setattr(story, key, value)
        
        story.updated_at = datetime.now()
        return True
    
    def delete_story(self, story_id: str) -> bool:
        """Delete a story"""
        if story_id in self.stories:
            del self.stories[story_id]
            return True
        return False
    
    # Character Management Methods
    def create_character(self, character_data: dict) -> Character:
        """Create a new character"""
        character_id = str(uuid.uuid4())
        character_data['id'] = character_id
        character = Character(**character_data)
        self.characters[character_id] = character
        return character
    
    def get_character(self, character_id: str) -> Optional[Character]:
        """Get character by ID"""
        return self.characters.get(character_id)
    
    def get_all_characters(self) -> List[Character]:
        """Get all characters"""
        return list(self.characters.values())
    
    def update_character(self, character_id: str, **kwargs) -> bool:
        """Update character details"""
        character = self.get_character(character_id)
        if not character:
            return False
        
        for key, value in kwargs.items():
            if hasattr(character, key) and value is not None:
                setattr(character, key, value)
        
        return True
    
    def delete_character(self, character_id: str) -> bool:
        """Delete a character"""
        if character_id in self.characters:
            del self.characters[character_id]
            # Remove from all stories
            for story in self.stories.values():
                story.characters = [c for c in story.characters if c.id != character_id]
            return True
        return False
    
    # Chapter Management Methods
    def create_chapter(self, story_id: str, title: str, content: str = "", status: ChapterStatus = ChapterStatus.DRAFT) -> Optional[Chapter]:
        """Create a new chapter"""
        story = self.get_story(story_id)
        if not story:
            return None
        
        chapter_id = str(uuid.uuid4())
        now = datetime.now()
        order = len(story.chapters) + 1
        
        chapter = Chapter(
            id=chapter_id,
            title=title,
            content=content,
            word_count=len(content.split()) if content else 0,
            status=status,
            order=order,
            created_at=now,
            updated_at=now
        )
        
        story.chapters.append(chapter)
        story.updated_at = now
        return chapter
    
    def get_chapter(self, story_id: str, chapter_id: str) -> Optional[Chapter]:
        """Get specific chapter"""
        story = self.get_story(story_id)
        if not story:
            return None
        
        for chapter in story.chapters:
            if chapter.id == chapter_id:
                return chapter
        return None
    
    def get_story_chapters(self, story_id: str) -> List[Chapter]:
        """Get all chapters for a story"""
        story = self.get_story(story_id)
        if not story:
            return []
        return sorted(story.chapters, key=lambda x: x.order)
    
    def update_chapter(self, story_id: str, chapter_id: str, **kwargs) -> bool:
        """Update chapter details"""
        story = self.get_story(story_id)
        if not story:
            return False
        
        for chapter in story.chapters:
            if chapter.id == chapter_id:
                for key, value in kwargs.items():
                    if hasattr(chapter, key) and value is not None:
                        setattr(chapter, key, value)
                
                # Update word count if content changed
                if 'content' in kwargs:
                    chapter.word_count = len(kwargs['content'].split()) if kwargs['content'] else 0
                
                chapter.updated_at = datetime.now()
                story.updated_at = datetime.now()
                return True
        return False
    
    def delete_chapter(self, story_id: str, chapter_id: str) -> bool:
        """Delete a chapter"""
        story = self.get_story(story_id)
        if not story:
            return False
        
        # Debug: Print chapter IDs for comparison
        print(f"DEBUG: Trying to delete chapter_id: {chapter_id}")
        print(f"DEBUG: Available chapter IDs: {[c.id for c in story.chapters]}")
        
        # Check if chapter exists before deletion
        original_count = len(story.chapters)
        story.chapters = [c for c in story.chapters if c.id != chapter_id]
        
        # If no chapters were removed, the chapter didn't exist
        if len(story.chapters) == original_count:
            print(f"DEBUG: No chapter found with ID {chapter_id}, returning False")
            return False
        
        print(f"DEBUG: Chapter {chapter_id} deleted successfully")
        # Reorder remaining chapters
        for i, chapter in enumerate(sorted(story.chapters, key=lambda x: x.order)):
            chapter.order = i + 1
        
        story.updated_at = datetime.now()
        return True
    
    # Relationship Management Methods
    def create_relationship(self, character1_id: str, character2_id: str, relationship_type: str, description: str = None, strength: int = None) -> Relationship:
        """Create a new character relationship"""
        relationship_id = str(uuid.uuid4())
        relationship = Relationship(
            id=relationship_id,
            character1_id=character1_id,
            character2_id=character2_id,
            type=relationship_type,
            description=description,
            strength=strength
        )
        self.relationships[relationship_id] = relationship
        return relationship
    
    def get_relationship(self, relationship_id: str) -> Optional[Relationship]:
        """Get relationship by ID"""
        return self.relationships.get(relationship_id)
    
    def get_all_relationships(self) -> List[Relationship]:
        """Get all relationships"""
        return list(self.relationships.values())
    
    def get_character_relationships(self, character_id: str) -> List[Relationship]:
        """Get all relationships for a character"""
        relationships = []
        for rel in self.relationships.values():
            if rel.character1_id == character_id or rel.character2_id == character_id:
                relationships.append(rel)
        return relationships
    
    def update_relationship(self, relationship_id: str, **kwargs) -> bool:
        """Update relationship details"""
        relationship = self.get_relationship(relationship_id)
        if not relationship:
            return False
        
        for key, value in kwargs.items():
            if hasattr(relationship, key) and value is not None:
                setattr(relationship, key, value)
        
        return True
    
    def delete_relationship(self, relationship_id: str) -> bool:
        """Delete a relationship"""
        if relationship_id in self.relationships:
            del self.relationships[relationship_id]
            return True
        return False

# Global story manager instance
story_manager = StoryManager()