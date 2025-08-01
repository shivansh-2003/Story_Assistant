from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from typing import List, Dict, Any
import os
from models import Character, StoryTheme
from dotenv import load_dotenv

load_dotenv()

class MockLLMService:
    """Mock LLM service for development/testing when GROQ_API_KEY is not available"""
    
    def __init__(self):
        pass
        
    def generate_story_continuation(self, 
                                 theme: StoryTheme,
                                 characters: List[Character],
                                 previous_content: str,
                                 user_choice: str = None,
                                 auto_continue: bool = False) -> str:
        """Generate mock story continuation"""
        char_names = [char.name for char in characters[:2]]  # Use first 2 characters
        
        if user_choice:
            return f"""Following the user's choice: "{user_choice}"
            
{char_names[0] if char_names else 'The protagonist'} decided to take action. The {theme.value} adventure continued as they faced new challenges in this mystical world. {"With " + char_names[1] if len(char_names) > 1 else "Alone"}, they ventured forward into the unknown.

The air was thick with magic and mystery. Every step brought new discoveries and dangers. This was just the beginning of an epic tale that would test their courage and determination.

[This is mock content - set GROQ_API_KEY environment variable for AI-generated content]"""
        else:
            return f"""The {theme.value} story continues automatically...

{char_names[0] if char_names else 'The hero'} found themselves in a crucial moment. The world around them seemed to hold its breath as important decisions loomed ahead. 

{"Together with " + char_names[1] + ", they" if len(char_names) > 1 else "They"} knew that their next actions would shape the destiny of everyone they cared about.

[This is mock content - set GROQ_API_KEY environment variable for AI-generated content]"""
    
    def edit_story_segment(self,
                          original_content: str,
                          edit_instruction: str,
                          context: str = "",
                          characters: List[Character] = None) -> str:
        """Edit story segment with mock response"""
        return f"""[EDITED] {original_content}

--- EDIT APPLIED ---
Edit instruction: {edit_instruction}

The content has been enhanced with more dramatic tension and character development. 

[This is mock edited content - set GROQ_API_KEY environment variable for AI-generated content]"""
    
    def generate_character_backstory(self, character: Character) -> str:
        """Generate mock character backstory"""
        return f"""{character.name} was born in a small village where {character.primary_trait.value} individuals were highly respected. From a young age, they showed exceptional talent in their chosen path.

Their {character.appearance.lower()} made them stand out among their peers. {"At " + str(character.age) + " years old, " if character.age else ""}they have dedicated their life to {character.occupation or "their calling"}.

{"Driven by " + character.motivation + ", " if character.motivation else ""}{character.name} continues to grow stronger each day, though they struggle with their tendency toward being {character.fatal_flaw or "overly cautious"}.

[This is mock backstory - set GROQ_API_KEY environment variable for AI-generated content]"""

class LLMService:
    def __init__(self, groq_api_key: str):
        self.llm = ChatGroq(
            groq_api_key=groq_api_key,
            model_name="llama-3.1-70b-versatile",
            temperature=0.7,
            max_tokens=1000
        )
        self.output_parser = StrOutputParser()
        
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
    
    def summarize_for_image(self, story_content: str) -> str:
        """Summarize story content for image generation"""
        
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", "Summarize story content into a clear visual description suitable for image generation."),
            ("human", """Story Content:
{content}

Create a concise visual summary (50-100 words) focusing on:
- Key characters and their appearance
- Setting and atmosphere
- Main action or scene
- Visual elements that would make a compelling image""")
        ])
        
        chain = prompt_template | self.llm | self.output_parser
        
        result = chain.invoke({"content": story_content})
        return result.strip()

# Initialize LLM service (will be set in FastAPI startup)
llm_service = None

def initialize_llm_service(groq_api_key: str):
    global llm_service
    if groq_api_key and groq_api_key != "your_groq_api_key_here":
        llm_service = LLMService(groq_api_key)
    else:
        print("🔄 Using Mock LLM Service for development (set GROQ_API_KEY for AI features)")
        llm_service = MockLLMService()