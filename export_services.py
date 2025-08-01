from fpdf import FPDF
from gtts import gTTS
import io
import base64
from typing import List
from models import Story, StorySegment
import tempfile
import os

class PDFExportService:
    def __init__(self):
        self.pdf = None
    
    def create_basic_pdf(self, story: Story) -> bytes:
        """Create basic PDF from story"""
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        
        # Title
        if story.title:
            pdf.set_font("Arial", "B", 16)
            pdf.cell(0, 10, story.title, ln=True, align="C")
            pdf.ln(10)
        
        # Theme
        pdf.set_font("Arial", "I", 12)
        pdf.cell(0, 10, f"Genre: {story.theme.value.title()}", ln=True)
        pdf.ln(5)
        
        # Characters section
        if story.characters:
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, "Characters:", ln=True)
            pdf.set_font("Arial", "", 12)
            
            for char in story.characters:
                char_info = f"• {char.name}"
                if char.age:
                    char_info += f" (Age: {char.age})"
                if char.occupation:
                    char_info += f" - {char.occupation}"
                pdf.multi_cell(0, 8, char_info)
                if char.appearance:
                    pdf.multi_cell(0, 6, f"  Description: {char.appearance}")
                pdf.ln(2)
            pdf.ln(5)
        
        # Story content
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Story:", ln=True)
        pdf.set_font("Arial", "", 12)
        
        # Add segments in order
        sorted_segments = sorted(story.segments, key=lambda x: x.order)
        if sorted_segments:
            for segment in sorted_segments:
                # Convert to latin-1 compatible text
                content = segment.content.encode('latin-1', 'replace').decode('latin-1')
                pdf.multi_cell(0, 8, content)
                pdf.ln(5)
        else:
            # Handle empty story
            if story.base_idea:
                pdf.multi_cell(0, 8, f"Story Idea: {story.base_idea.encode('latin-1', 'replace').decode('latin-1')}")
                pdf.ln(5)
            pdf.multi_cell(0, 8, "[Story content will appear here as it's generated]")
        
        return pdf.output(dest='S').encode('latin-1')
    
    def create_pdf_base64(self, story: Story) -> str:
        """Create PDF and return as base64 string"""
        pdf_bytes = self.create_basic_pdf(story)
        return base64.b64encode(pdf_bytes).decode('utf-8')

class AudioExportService:
    def __init__(self):
        self.supported_languages = {
            "en": "English",
            "es": "Spanish", 
            "fr": "French",
            "de": "German",
            "it": "Italian",
            "pt": "Portuguese",
            "ru": "Russian",
            "ja": "Japanese",
            "ko": "Korean",
            "zh": "Chinese"
        }
    
    def create_audio_from_story(self, story: Story, language: str = "en") -> bytes:
        """Create audio file from story content"""
        if language not in self.supported_languages:
            language = "en"
        
        # Combine all story segments
        sorted_segments = sorted(story.segments, key=lambda x: x.order)
        full_text = " ".join([segment.content for segment in sorted_segments])
        
        # Handle empty story - use base idea or placeholder
        if not full_text.strip():
            if story.base_idea:
                full_text = f"Story concept: {story.base_idea}. This story is still being written."
            else:
                full_text = "This story is currently empty and waiting for content to be generated."
        
        # Create TTS
        tts = gTTS(text=full_text, lang=language, slow=False)
        
        # Save to temporary file and read bytes
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
            tts.save(temp_file.name)
            temp_file.seek(0)
            
            with open(temp_file.name, 'rb') as audio_file:
                audio_bytes = audio_file.read()
            
            # Clean up temp file
            os.unlink(temp_file.name)
            
        return audio_bytes
    
    def create_audio_base64(self, story: Story, language: str = "en") -> str:
        """Create audio and return as base64 string"""
        audio_bytes = self.create_audio_from_story(story, language)
        return base64.b64encode(audio_bytes).decode('utf-8')
    
    def get_supported_languages(self) -> dict:
        """Get supported languages"""
        return self.supported_languages

# Global service instances
pdf_service = PDFExportService()
audio_service = AudioExportService()