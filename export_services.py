from fpdf import FPDF
from gtts import gTTS
import io
import base64
from typing import List
from models import Story, StorySegment
import tempfile
import os
import re

class PDFExportService:
    def __init__(self):
        self.pdf = None
    
    def _clean_text_for_pdf(self, text: str) -> str:
        """Clean text for PDF compatibility"""
        if not text:
            return ""
        
        # Replace bullet points and other special characters
        text = text.replace('•', '-')  # Replace bullet with dash
        text = text.replace('"', '"').replace('"', '"')  # Replace smart quotes
        text = text.replace(''', "'").replace(''', "'")  # Replace smart apostrophes
        text = text.replace('—', '-').replace('–', '-')  # Replace em/en dashes
        text = text.replace('…', '...')  # Replace ellipsis
        
        # Remove other problematic Unicode characters but preserve basic text
        # Keep letters, numbers, basic punctuation, and spaces
        import re
        text = re.sub(r'[^\x20-\x7E]', ' ', text)  # Keep only printable ASCII
        
        # Clean up extra whitespace
        text = ' '.join(text.split())
        
        # Ensure text isn't too long for PDF
        if len(text) > 1000:
            text = text[:997] + "..."
        
        return text
    
    def create_basic_pdf(self, story: Story) -> bytes:
        """Create basic PDF from story"""
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        
        try:
            # Title
            if story.title:
                pdf.set_font("Arial", "B", 16)
                clean_title = self._clean_text_for_pdf(story.title)
                if clean_title:  # Only add if not empty
                    pdf.cell(0, 10, clean_title, ln=True, align="C")
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
                    char_info = f"- {char.name}"  # Use dash instead of bullet
                    if char.age:
                        char_info += f" (Age: {char.age})"
                    if char.occupation:
                        char_info += f" - {char.occupation}"
                    
                    # Clean character info
                    char_info = self._clean_text_for_pdf(char_info)
                    if char_info:  # Only add if not empty
                        pdf.multi_cell(0, 8, char_info)
                    
                    if char.appearance:
                        appearance_text = self._clean_text_for_pdf(f"  Description: {char.appearance}")
                        if appearance_text:  # Only add if not empty
                            pdf.multi_cell(0, 6, appearance_text)
                    pdf.ln(2)
                pdf.ln(5)
            
            # Story content
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, "Story:", ln=True)
            pdf.set_font("Arial", "", 12)
            
            # Add chapters first if they exist
            if story.chapters:
                sorted_chapters = sorted(story.chapters, key=lambda x: x.order)
                for chapter in sorted_chapters:
                    # Chapter title
                    pdf.set_font("Arial", "B", 13)
                    clean_title = self._clean_text_for_pdf(chapter.title)
                    if clean_title:
                        pdf.cell(0, 10, clean_title, ln=True)
                        pdf.ln(3)
                    
                    # Chapter content
                    pdf.set_font("Arial", "", 12)
                    if chapter.content:
                        clean_content = self._clean_text_for_pdf(chapter.content)
                        if clean_content:
                            pdf.multi_cell(0, 8, clean_content)
                    else:
                        pdf.multi_cell(0, 8, "[Chapter content to be written]")
                    pdf.ln(8)
            
            # Add segments if no chapters exist (backward compatibility)
            elif story.segments:
                sorted_segments = sorted(story.segments, key=lambda x: x.order)
                for segment in sorted_segments:
                    # Clean and add content
                    clean_content = self._clean_text_for_pdf(segment.content)
                    if clean_content:  # Only add if not empty
                        pdf.multi_cell(0, 8, clean_content)
                        pdf.ln(5)
            else:
                # Handle empty story
                if story.base_idea:
                    clean_idea = self._clean_text_for_pdf(f"Story Idea: {story.base_idea}")
                    if clean_idea:  # Only add if not empty
                        pdf.multi_cell(0, 8, clean_idea)
                        pdf.ln(5)
                pdf.multi_cell(0, 8, "[Story content will appear here as it's generated]")
            
            # Return PDF bytes
            pdf_output = pdf.output(dest='S')
        
        except Exception as e:
            # If PDF generation fails, create a minimal PDF
            print(f"PDF generation error: {e}")
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", "", 12)
            pdf.cell(0, 10, f"Story: {story.theme.value.title()}", ln=True)
            pdf.ln(5)
            pdf.multi_cell(0, 8, "Story content is being generated...")
            pdf_output = pdf.output(dest='S')
        
        # Handle different FPDF versions and ensure we return bytes
        if isinstance(pdf_output, str):
            return pdf_output.encode('latin-1')
        elif isinstance(pdf_output, bytearray):
            return bytes(pdf_output)
        else:
            return pdf_output
    
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
        
        # Combine chapters first if they exist
        full_text = ""
        if story.chapters:
            sorted_chapters = sorted(story.chapters, key=lambda x: x.order)
            chapter_texts = []
            for chapter in sorted_chapters:
                if chapter.content:
                    chapter_texts.append(f"{chapter.title}. {chapter.content}")
            full_text = " ".join(chapter_texts)
        
        # Fall back to segments if no chapters (backward compatibility)
        if not full_text.strip() and story.segments:
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