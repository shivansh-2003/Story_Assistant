from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from typing import List, Dict, Any
import os
from models import Character, StoryTheme
from dotenv import load_dotenv

load_dotenv()

class LLMService:
    def __init__(self, groq_api_key: str):
        if not groq_api_key:
            raise ValueError("GROQ_API_KEY is required")
        
        print(f"🚀 Initializing LLM Service with API key: {groq_api_key[:10]}...")
        
        self.llm = ChatGroq(
            groq_api_key=groq_api_key,
            model_name="llama-3.1-8b-instant",
            temperature=0.7,
            max_tokens=1000
        )
        self.output_parser = StrOutputParser()
        print("✅ LLM Service initialized successfully")
        
    def _format_characters(self, characters: List[Character]) -> str:
        """Format characters for prompt"""
        if not characters:
            return "No specific characters defined."
            
        char_descriptions = []
        for char in characters:
            desc = f"- {char.name}: {char.primary_trait.value} character"
            if char.age:
                desc += f", age {char.age}"
            if char.occupation:
                desc += f", works as {char.occupation}"
            desc += f". Appearance: {char.appearance}"
            if char.motivation:
                desc += f". Motivation: {char.motivation}"
            if char.speaking_style:
                desc += f". Speaks in a {char.speaking_style.value} manner"
            char_descriptions.append(desc)
            
        return "\n".join(char_descriptions)
    
    def generate_story_continuation(self, 
                                 theme: StoryTheme,
                                 characters: List[Character],
                                 previous_content: str,
                                 user_choice: str = None,
                                 auto_continue: bool = False) -> str:
        """Generate story continuation"""
        
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", """You are a creative storyteller. Generate engaging story continuations that:
            1. Maintain consistency with previous content
            2. Include character personalities and relationships
            3. Match the specified theme and tone
            4. Create compelling narrative flow
            5. Keep responses between 200-400 words"""),
            ("human", """Theme: {theme}

Characters:
{characters}

Previous Story:
{previous_content}

{choice_instruction}

Continue the story naturally, incorporating the characters and maintaining the theme.""")
        ])
        
        if auto_continue:
            choice_instruction = "Continue the story automatically based on the natural flow of events."
        else:
            choice_instruction = f"User's choice/direction: {user_choice}"
            
        chain = (
            {
                "theme": lambda x: x["theme"],
                "characters": lambda x: self._format_characters(x["characters"]),
                "previous_content": lambda x: x["previous_content"],
                "choice_instruction": lambda x: x["choice_instruction"]
            }
            | prompt_template
            | self.llm
            | self.output_parser
        )
        
        result = chain.invoke({
            "theme": theme.value,
            "characters": characters,
            "previous_content": previous_content,
            "choice_instruction": choice_instruction
        })
        
        return result.strip()
    
    def edit_story_segment(self,
                          original_content: str,
                          edit_instruction: str,
                          context: str = "",
                          characters: List[Character] = None) -> str:
        """Edit a story segment based on user instruction"""
        
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", """You are a story editor. Edit the given text according to the user's instructions while:
            1. Maintaining narrative consistency
            2. Preserving character voices and personalities
            3. Keeping the same general length unless specified
            4. Ensuring smooth flow with surrounding context"""),
            ("human", """Original Content:
{original_content}

Surrounding Context:
{context}

Characters:
{characters}

Edit Instruction: {edit_instruction}

Provide the edited version of the content:""")
        ])
        
        chain = (
            {
                "original_content": lambda x: x["original_content"],
                "context": lambda x: x["context"],
                "characters": lambda x: self._format_characters(x["characters"]) if x["characters"] else "",
                "edit_instruction": lambda x: x["edit_instruction"]
            }
            | prompt_template
            | self.llm
            | self.output_parser
        )
        
        result = chain.invoke({
            "original_content": original_content,
            "context": context,
            "characters": characters or [],
            "edit_instruction": edit_instruction
        })
        
        return result.strip()
    
    def generate_character_backstory(self, character: Character) -> str:
        """Generate detailed backstory for a character"""
        
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", "You are a character development specialist. Create rich, consistent backstories."),
            ("human", """Character: {name}
Age: {age}
Occupation: {occupation}
Primary Trait: {primary_trait}
Appearance: {appearance}
Motivation: {motivation}

Generate a compelling backstory (150-200 words) that explains how this character became who they are.""")
        ])
        
        chain = prompt_template | self.llm | self.output_parser
        
        result = chain.invoke({
            "name": character.name,
            "age": character.age or "Unknown",
            "occupation": character.occupation or "Unknown",
            "primary_trait": character.primary_trait.value,
            "appearance": character.appearance,
            "motivation": character.motivation or "Unknown"
        })
        
        return result.strip()
    
    def generate_chapter_content(self, 
                               chapter_title: str,
                               story_context: str,
                               characters: List[Character],
                               theme: StoryTheme,
                               target_length: str = "medium") -> str:
        """Generate content for a specific chapter"""
        
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", """You are a creative storyteller writing a specific chapter. Generate engaging chapter content that:
            1. Matches the chapter title and story context
            2. Incorporates character personalities consistently
            3. Maintains the story's theme and tone
            4. Creates compelling scenes and dialogue
            5. Advances the plot meaningfully
            6. Length: {target_length} (short: 300-500 words, medium: 500-800 words, long: 800-1200 words)"""),
            ("human", """Chapter Title: {chapter_title}
            
Story Context/Previous Chapters:
{story_context}

Theme: {theme}

Characters:
{characters}

Target Length: {target_length}

Write the complete chapter content:""")
        ])
        
        chain = (
            {
                "chapter_title": lambda x: x["chapter_title"],
                "story_context": lambda x: x["story_context"],
                "theme": lambda x: x["theme"],
                "characters": lambda x: self._format_characters(x["characters"]),
                "target_length": lambda x: x["target_length"]
            }
            | prompt_template
            | self.llm
            | self.output_parser
        )
        
        result = chain.invoke({
            "chapter_title": chapter_title,
            "story_context": story_context,
            "theme": theme.value,
            "characters": characters,
            "target_length": target_length
        })
        
        return result.strip()

def initialize_llm_service():
    """Initialize the LLM service with Groq API key"""
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise ValueError("GROQ_API_KEY environment variable must be set")
    
    print(f"🔧 Initializing LLM service...")
    service = LLMService(groq_api_key)
    print(f"✅ LLM service initialized: {type(service).__name__}")
    return service