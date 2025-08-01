import uuid
from typing import Dict, List, Optional
from models import Story, StorySegment, Character, StoryTheme
import json

class StoryManager:
    def __init__(self):
        self.stories: Dict[str, Story] = {}
        
    def create_story(self, base_idea: str, theme: StoryTheme, characters: List[Character] = None) -> Story:
        """Create a new story"""
        story_id = str(uuid.uuid4())
        story = Story(
            id=story_id,
            theme=theme,
            base_idea=base_idea,
            characters=characters or [],
            segments=[],
            is_completed=False
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

# Global story manager instance
story_manager = StoryManager()