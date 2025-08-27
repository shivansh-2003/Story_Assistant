# agents/visual_storytelling.py
from typing import Dict, Any, List, Optional
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
import json
import logging
import re

from .base_agent import BaseAgent
from models.generation_models import (
    AgentContext, AgentType, ImageType, PosterType
)
from services.vector_service import VectorService

logger = logging.getLogger(__name__)

class VisualStorytellingAgent(BaseAgent):
    """
    Visual Storytelling Agent
    
    Responsibilities:
    - Chapter-specific scene visualization (toggleable)
    - Character progression visual tracking
    - Story poster/cover art generation
    - Marketing material creation
    - Visual style consistency across unlimited content
    - Image generation budget management
    - Scene analysis for visual opportunities
    - Character appearance consistency
    """
    
    def __init__(self, vector_service: VectorService):
        super().__init__(
            agent_type=AgentType.VISUAL_STORYTELLING,
            vector_service=vector_service
        )
        self.character_visual_profiles: Dict[str, Dict[str, Any]] = {}
        self.visual_style_guide: Dict[str, Any] = {}
        self.generation_history: List[Dict[str, Any]] = []
    
    def _get_agent_role_description(self) -> str:
        return """
        As the Visual Storytelling Agent, you create compelling visual content that enhances 
        the narrative experience and maintains visual consistency across the story.
        
        Your key responsibilities:
        1. Analyze story content for visual generation opportunities
        2. Create detailed image generation prompts that capture scene essence
        3. Maintain character visual consistency across all generated images
        4. Generate story posters and marketing materials
        5. Adapt visual style to match genre and story tone
        6. Manage visual element continuity across chapters
        7. Create scene-specific images that enhance reader immersion
        8. Design promotional visual content for story marketing
        """
    
    async def _execute_task(self, context: AgentContext) -> Dict[str, Any]:
        """
        Execute Visual Storytelling specific tasks
        """
        task_data = context.agent_specific_data
        task_type = task_data.get("task_type", "analyze_scene")
        
        if task_type == "analyze_scene":
            return await self._analyze_scene(context)
        elif task_type == "generate_character_portrait":
            return await self._generate_character_portrait(context)
        elif task_type == "generate_story_poster":
            return await self._generate_story_poster(context)
        elif task_type == "analyze_visual_opportunities":
            return await self._analyze_visual_opportunities(context)
        elif task_type == "create_visual_style_guide":
            return await self._create_visual_style_guide(context)
        elif task_type == "check_visual_consistency":
            return await self._check_visual_consistency(context)
        else:
            raise ValueError(f"Unknown task type: {task_type}")
    
    async def _analyze_scene(self, context: AgentContext) -> Dict[str, Any]:
        """
        Generate an image for a specific scene
        """
        logger.info(f"Generating scene image for task {context.task_id}")
        
        # 1. Analyze the content for visual elements
        scene_analysis = await self._analyze_scene_content(context)
        
        # 2. Create detailed image prompt
        image_prompt = await self._create_scene_image_prompt(context, scene_analysis)
        
        # 3. Ensure character consistency
        character_consistency = await self._ensure_character_consistency(context, scene_analysis)
        
        # 4. Generate final prompt with style guidance
        final_prompt = await self._create_final_image_prompt(
            context, image_prompt, character_consistency
        )
        
        # 5. Store generation metadata
        await self._store_visual_generation_metadata(context, final_prompt, scene_analysis)
        
        return {
            "image_generation_prompt": final_prompt["prompt"],
            "negative_prompt": final_prompt.get("negative_prompt", ""),
            "style_parameters": final_prompt.get("style_parameters", {}),
            "character_descriptions": character_consistency.get("character_descriptions", {}),
            "scene_elements": scene_analysis.get("visual_elements", []),
            "composition_notes": final_prompt.get("composition_notes", ""),
            "technical_specifications": final_prompt.get("technical_specs", {}),
            "consistency_requirements": character_consistency.get("consistency_notes", [])
        }
    
    async def _analyze_scene_content(self, context: AgentContext) -> Dict[str, Any]:
        """
        Analyze content to extract visual elements for scene generation
        """
        content = context.agent_specific_data.get("content", "")
        story_metadata = context.story_context.story_metadata
        
        analysis_prompt = """
        Analyze this story content to identify visual elements for image generation:
        
        Content: {content}
        
        Story Context:
        - Genre: {genre}
        - Setting: {setting}
        - Time Period: {time_period}
        - Writing Style: {writing_style}
        
        Extract visual elements in JSON format:
        {{
            "primary_scene": "main visual focus of the content",
            "setting_details": {{
                "location": "where the scene takes place",
                "time_of_day": "time/lighting conditions",
                "weather": "atmospheric conditions",
                "environment_mood": "overall environmental feeling"
            }},
            "characters_present": [
                {{
                    "name": "character name",
                    "role_in_scene": "what they're doing",
                    "emotional_state": "their current emotion",
                    "position": "where they are in the scene"
                }}
            ],
            "visual_elements": [
                {{
                    "element": "specific visual element",
                    "importance": "high|medium|low",
                    "description": "detailed description"
                }}
            ],
            "mood_and_atmosphere": "overall emotional tone of the scene",
            "key_actions": ["important actions happening in the scene"],
            "focal_points": ["what should draw the viewer's attention"],
            "composition_suggestions": "how the image should be composed"
        }}
        """
        
        context_vars = {
            "content": content[:1500],
            "genre": story_metadata.get("genre", "general"),
            "setting": story_metadata.get("setting_location", "unspecified"),
            "time_period": story_metadata.get("setting_time_period", "unspecified"),
            "writing_style": story_metadata.get("writing_style", "balanced")
        }
        
        result = await self._generate_with_llm(
            analysis_prompt,
            context_vars,
            JsonOutputParser()
        )
        
        return result
    
    async def _create_scene_image_prompt(
        self, 
        context: AgentContext, 
        scene_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create detailed image generation prompt based on scene analysis
        """
        genre = context.story_context.story_metadata.get("genre", "general")
        image_style = context.story_context.image_settings.get("image_style", "realistic")
        
        prompt_creation = """
        Create a detailed image generation prompt based on the scene analysis:
        
        Scene Analysis: {scene_analysis}
        Genre: {genre}
        Image Style: {image_style}
        
        Create image prompt in JSON format:
        {{
            "main_prompt": "detailed, vivid description for image generation",
            "composition_details": "specific composition and framing instructions",
            "lighting_description": "lighting conditions and mood",
            "color_palette": "dominant colors and color mood",
            "art_style_modifiers": "style keywords for the specified image style",
            "detail_level": "level of detail to include",
            "perspective": "camera angle and viewpoint",
            "technical_quality": "quality and technical specifications"
        }}
        """
        
        context_vars = {
            "scene_analysis": json.dumps(scene_analysis, indent=2),
            "genre": genre,
            "image_style": image_style
        }
        
        result = await self._generate_with_llm(
            prompt_creation,
            context_vars,
            JsonOutputParser()
        )
        
        return result
    
    async def _ensure_character_consistency(
        self,
        context: AgentContext,
        scene_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Ensure character visual consistency across generated images
        """
        characters_present = scene_analysis.get("characters_present", [])
        
        if not characters_present:
            return {"character_descriptions": {}, "consistency_notes": []}
        
        character_consistency = {
            "character_descriptions": {},
            "consistency_notes": []
        }
        
        for character in characters_present:
            char_name = character.get("name", "")
            if char_name:
                # Get established character appearance
                char_profile = await self._get_character_visual_profile(char_name, context)
                
                if char_profile:
                    character_consistency["character_descriptions"][char_name] = char_profile
                    character_consistency["consistency_notes"].append(
                        f"Maintain established appearance for {char_name}: {char_profile.get('key_features', '')}"
                    )
                else:
                    # Create new character profile from story context
                    new_profile = await self._create_character_visual_profile(char_name, context)
                    if new_profile:
                        character_consistency["character_descriptions"][char_name] = new_profile
                        self.character_visual_profiles[char_name] = new_profile
        
        return character_consistency
    
    async def _create_final_image_prompt(
        self,
        context: AgentContext,
        image_prompt: Dict[str, Any],
        character_consistency: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create final comprehensive image generation prompt
        """
        final_prompt_creation = """
        Combine all elements into a final, comprehensive image generation prompt:
        
        Base Image Prompt: {base_prompt}
        Character Descriptions: {character_descriptions}
        Story Genre: {genre}
        Image Style: {image_style}
        
        Create final prompt in JSON format:
        {{
            "prompt": "complete, detailed image generation prompt",
            "negative_prompt": "what to avoid in the image",
            "style_parameters": {{
                "art_style": "specific art style",
                "quality_level": "quality descriptors",
                "composition": "composition guidelines"
            }},
            "technical_specs": {{
                "aspect_ratio": "recommended aspect ratio",
                "resolution": "recommended resolution",
                "style_strength": "style application strength"
            }},
            "composition_notes": "additional composition guidance"
        }}
        """
        
        context_vars = {
            "base_prompt": json.dumps(image_prompt),
            "character_descriptions": json.dumps(character_consistency.get("character_descriptions", {})),
            "genre": context.story_context.story_metadata.get("genre", "general"),
            "image_style": context.story_context.image_settings.get("image_style", "realistic")
        }
        
        result = await self._generate_with_llm(
            final_prompt_creation,
            context_vars,
            JsonOutputParser()
        )
        
        return result
    
    async def _generate_character_portrait(self, context: AgentContext) -> Dict[str, Any]:
        """
        Generate a character portrait image
        """
        character_name = context.agent_specific_data.get("character_name", "")
        if not character_name:
            raise ValueError("Character name required for portrait generation")
        
        # Get character information
        character_info = await self._get_character_information(character_name, context)
        
        # Create character portrait prompt
        portrait_prompt = await self._create_character_portrait_prompt(character_info, context)
        
        return {
            "image_generation_prompt": portrait_prompt["prompt"],
            "negative_prompt": portrait_prompt.get("negative_prompt", ""),
            "character_info": character_info,
            "style_parameters": portrait_prompt.get("style_parameters", {}),
            "technical_specifications": portrait_prompt.get("technical_specs", {})
        }
    
    async def _generate_story_poster(self, context: AgentContext) -> Dict[str, Any]:
        """
        Generate story poster/cover art
        """
        poster_type = context.agent_specific_data.get("poster_type", PosterType.CHARACTER_FOCUSED)
        
        # Analyze story for poster elements
        poster_analysis = await self._analyze_story_for_poster(context)
        
        # Create poster design concepts
        poster_concepts = await self._create_poster_concepts(context, poster_analysis, poster_type)
        
        # Generate final poster prompts
        poster_prompts = await self._create_poster_prompts(context, poster_concepts)
        
        return {
            "poster_concepts": poster_concepts,
            "poster_prompts": poster_prompts,
            "design_rationale": poster_analysis.get("design_rationale", ""),
            "marketing_appeal": poster_analysis.get("marketing_elements", []),
            "variant_suggestions": poster_concepts.get("variants", [])
        }
    
    async def _analyze_story_for_poster(self, context: AgentContext) -> Dict[str, Any]:
        """
        Analyze story content to determine poster design elements
        """
        story_metadata = context.story_context.story_metadata
        
        poster_analysis_prompt = """
        Analyze this story to determine the best poster/cover art approach:
        
        Story Information:
        - Title: {title}
        - Genre: {genre}
        - Target Audience: {target_audience}
        - Writing Style: {writing_style}
        - Themes: {themes}
        - Setting: {setting}
        
        Character Information: {characters}
        
        Provide poster analysis in JSON format:
        {{
            "visual_themes": ["key visual themes that represent the story"],
            "color_palette_suggestions": ["color schemes that fit the story mood"],
            "main_character_focus": "which character(s) should be featured",
            "setting_elements": ["key setting elements to include"],
            "mood_descriptors": ["words that describe the story's emotional tone"],
            "genre_conventions": ["visual elements expected for this genre"],
            "target_audience_appeal": ["visual elements that appeal to target audience"],
            "marketing_elements": ["elements that would make the poster marketable"],
            "design_rationale": "explanation of the overall design approach"
        }}
        """
        
        context_vars = {
            "title": context.agent_specific_data.get("story_title", "Untitled Story"),
            "genre": story_metadata.get("genre", "general"),
            "target_audience": story_metadata.get("target_audience", "adult"),
            "writing_style": story_metadata.get("writing_style", "balanced"),
            "themes": ", ".join(story_metadata.get("themes", [])),
            "setting": story_metadata.get("setting_location", "unspecified"),
            "characters": json.dumps(context.story_context.characters[:3])  # Top 3 characters
        }
        
        result = await self._generate_with_llm(
            poster_analysis_prompt,
            context_vars,
            JsonOutputParser()
        )
        
        return result
    
    async def _create_poster_concepts(
        self,
        context: AgentContext,
        poster_analysis: Dict[str, Any],
        poster_type: PosterType
    ) -> Dict[str, Any]:
        """
        Create poster design concepts based on analysis
        """
        concept_creation_prompt = """
        Create poster design concepts based on the analysis and poster type:
        
        Poster Analysis: {poster_analysis}
        Poster Type: {poster_type}
        Genre: {genre}
        
        Create design concepts in JSON format:
        {{
            "primary_concept": {{
                "composition": "main composition approach",
                "visual_hierarchy": "how elements are prioritized visually",
                "character_treatment": "how characters are presented",
                "text_placement": "where title and text should go",
                "background_approach": "background design strategy"
            }},
            "color_scheme": {{
                "primary_colors": ["main colors"],
                "accent_colors": ["accent colors"],
                "mood": "emotional tone of colors"
            }},
            "typography_style": "recommended typography approach",
            "variants": [
                {{
                    "variant_name": "name of the variant",
                    "key_differences": "how this differs from primary concept"
                }}
            ],
            "marketing_considerations": ["elements that enhance marketability"]
        }}
        """
        
        context_vars = {
            "poster_analysis": json.dumps(poster_analysis, indent=2),
            "poster_type": poster_type.value,
            "genre": context.story_context.story_metadata.get("genre", "general")
        }
        
        result = await self._generate_with_llm(
            concept_creation_prompt,
            context_vars,
            JsonOutputParser()
        )
        
        return result
    
    async def _create_poster_prompts(
        self,
        context: AgentContext,
        poster_concepts: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Create final image generation prompts for posters
        """
        poster_prompt_creation = """
        Create detailed image generation prompts for the poster concepts:
        
        Poster Concepts: {poster_concepts}
        Story Title: {title}
        Genre: {genre}
        
        Create poster prompts in JSON format:
        {{
            "main_poster_prompt": {{
                "prompt": "detailed prompt for main poster design",
                "negative_prompt": "what to avoid",
                "style_parameters": "style specifications",
                "composition_notes": "composition guidelines"
            }},
            "variant_prompts": [
                {{
                    "variant_name": "variant identifier",
                    "prompt": "detailed prompt for this variant",
                    "key_differences": "what makes this variant unique"
                }}
            ]
        }}
        """
        
        context_vars = {
            "poster_concepts": json.dumps(poster_concepts, indent=2),
            "title": context.agent_specific_data.get("story_title", "Untitled Story"),
            "genre": context.story_context.story_metadata.get("genre", "general")
        }
        
        result = await self._generate_with_llm(
            poster_prompt_creation,
            context_vars,
            JsonOutputParser()
        )
        
        return result
    
    async def _get_character_visual_profile(
        self, 
        character_name: str, 
        context: AgentContext
    ) -> Optional[Dict[str, Any]]:
        """
        Get established visual profile for a character
        """
        # Check local cache first
        if character_name in self.character_visual_profiles:
            return self.character_visual_profiles[character_name]
        
        # Search vector database for character visual information
        try:
            character_docs = await self._get_relevant_context(
                context.story_context,
                f"character {character_name} appearance visual description",
                "character",
                max_results=3
            )
            
            if character_docs:
                # Extract visual information from documents
                profile = self._extract_visual_profile_from_docs(character_docs)
                self.character_visual_profiles[character_name] = profile
                return profile
            
            return None
            
        except Exception as e:
            logger.warning(f"Failed to get character visual profile for {character_name}: {e}")
            return None
    
    async def _create_character_visual_profile(
        self, 
        character_name: str, 
        context: AgentContext
    ) -> Optional[Dict[str, Any]]:
        """
        Create visual profile for character from story context
        """
        # Find character in story context
        character_info = None
        for char in context.story_context.characters:
            if char.get("name", "") == character_name:
                character_info = char
                break
        
        if not character_info:
            return None
        
        profile_creation_prompt = """
        Create a visual profile for this character based on their information:
        
        Character Information: {character_info}
        Genre: {genre}
        Art Style: {art_style}
        
        Create visual profile in JSON format:
        {{
            "key_features": "most distinctive visual features",
            "physical_description": "detailed physical appearance",
            "clothing_style": "typical clothing and style",
            "color_associations": ["colors associated with this character"],
            "distinguishing_marks": ["scars, tattoos, unique features"],
            "posture_and_bearing": "how they carry themselves",
            "expression_tendencies": "typical facial expressions",
            "art_style_notes": "how to render this character in the chosen art style"
        }}
        """
        
        context_vars = {
            "character_info": json.dumps(character_info),
            "genre": context.story_context.story_metadata.get("genre", "general"),
            "art_style": context.story_context.image_settings.get("image_style", "realistic")
        }
        
        try:
            result = await self._generate_with_llm(
                profile_creation_prompt,
                context_vars,
                JsonOutputParser()
            )
            
            return result
            
        except Exception as e:
            logger.warning(f"Failed to create visual profile for {character_name}: {e}")
            return None
    
    def _extract_visual_profile_from_docs(self, docs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extract visual profile information from vector database documents
        """
        profile = {
            "key_features": "",
            "physical_description": "",
            "clothing_style": "",
            "color_associations": [],
            "distinguishing_marks": []
        }
        
        for doc in docs:
            content = doc.get("content", "")
            metadata = doc.get("metadata", {})
            
            # Extract visual information from content and metadata
            # This is a simplified extraction - in a full implementation,
            # you'd use more sophisticated NLP techniques
            if "appearance" in content.lower() or "looks" in content.lower():
                profile["physical_description"] += content + " "
            
            if "clothing" in content.lower() or "wearing" in content.lower():
                profile["clothing_style"] += content + " "
        
        # Clean up extracted information
        for key in ["physical_description", "clothing_style"]:
            if profile[key]:
                profile[key] = profile[key].strip()
        
        return profile
    
    async def _store_visual_generation_metadata(
        self,
        context: AgentContext,
        final_prompt: Dict[str, Any],
        scene_analysis: Dict[str, Any]
    ):
        """
        Store visual generation metadata for consistency tracking
        """
        try:
            metadata = {
                "story_id": str(context.story_context.story_id),
                "chapter_id": str(context.story_context.current_chapter_id),
                "agent_type": "visual_storytelling",
                "generation_type": "scene_image",
                "prompt_used": final_prompt.get("prompt", ""),
                "scene_elements": scene_analysis.get("visual_elements", []),
                "characters_included": [char.get("name", "") for char in scene_analysis.get("characters_present", [])],
                "timestamp": context.task_id
            }
            
            await self._store_result_in_vector_db(
                content=final_prompt.get("prompt", ""),
                metadata=metadata,
                collection_name="generation_embeddings"
            )
            
            # Add to local generation history
            self.generation_history.append({
                "task_id": context.task_id,
                "metadata": metadata,
                "prompt": final_prompt
            })
            
        except Exception as e:
            logger.warning(f"Failed to store visual generation metadata: {e}")
    
    async def _analyze_visual_opportunities(self, context: AgentContext) -> Dict[str, Any]:
        """
        Analyze content for visual generation opportunities
        """
        content = context.agent_specific_data.get("content", "")
        
        opportunity_analysis_prompt = """
        Analyze this story content for visual generation opportunities:
        
        Content: {content}
        Genre: {genre}
        Image Settings: {image_settings}
        
        Identify opportunities in JSON format:
        {{
            "scene_opportunities": [
                {{
                    "scene_description": "what scene could be visualized",
                    "visual_appeal": "high|medium|low",
                    "complexity": "simple|moderate|complex",
                    "key_elements": ["main visual elements"]
                }}
            ],
            "character_opportunities": ["characters that could be portrayed"],
            "setting_opportunities": ["settings that could be visualized"],
            "mood_opportunities": ["atmospheric moments suitable for images"],
            "priority_ranking": ["ordered list of best opportunities"],
            "generation_suggestions": ["specific suggestions for image generation"]
        }}
        """
        
        context_vars = {
            "content": content[:1500],
            "genre": context.story_context.story_metadata.get("genre", "general"),
            "image_settings": json.dumps(context.story_context.image_settings)
        }
        
        result = await self._generate_with_llm(
            opportunity_analysis_prompt,
            context_vars,
            JsonOutputParser()
        )
        
        return result
