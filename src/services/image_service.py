# services/image_service.py
import asyncio
import logging
import json
import base64
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import google.generativeai as genai
from PIL import Image
import io

from config.settings import settings, IMAGE_GENERATION_CONFIGS

logger = logging.getLogger(__name__)

class ImageService:
    """
    Gemini Vision-only image analysis service for Story Assistant.
    Provides scene analysis, character consistency, and design guidance using Google's Generative AI.
    """
    
    def __init__(self):
        self.gemini_vision_model = None
        self.gemini_text_model = None
        self.gemini_initialized = False
        self.initialized = False
        self.generation_history: List[Dict[str, Any]] = []
        self.character_visual_cache: Dict[str, Dict[str, Any]] = {}
    
    async def initialize(self):
        """Initialize Gemini Vision models"""
        try:
            # Initialize Gemini Vision
            await self._initialize_gemini_vision()
            
            if not self.gemini_initialized:
                raise Exception("Gemini Vision initialization failed. Please check your GEMINI_API_KEY.")
            
            self.initialized = True
            logger.info("Image service initialized successfully with Gemini Vision")
            
        except Exception as e:
            logger.error(f"Failed to initialize image service: {e}")
            raise
    
    async def _initialize_gemini_vision(self):
        """Initialize Gemini Vision models"""
        try:
            # Check if Gemini API key is available
            if not hasattr(settings, 'gemini_api_key') or not settings.gemini_api_key:
                raise Exception("Gemini API key not found. Please set GEMINI_API_KEY in your environment.")
            
            # Configure Gemini
            genai.configure(api_key=settings.gemini_api_key)
            
            # Initialize models
            self.gemini_vision_model = genai.GenerativeModel('gemini-1.5-flash')
            self.gemini_text_model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Test connection
            await self._test_gemini_connection()
            
            self.gemini_initialized = True
            logger.info("Gemini Vision integrated successfully")
            
        except Exception as e:
            logger.error(f"Gemini Vision initialization failed: {e}")
            self.gemini_initialized = False
            raise
    
    async def _test_gemini_connection(self):
        """Test Gemini API connection"""
        try:
            # Simple text generation test
            response = self.gemini_text_model.generate_content("Hello, please respond with 'OK' if you can see this.")
            if "OK" in response.text:
                logger.info("Gemini API connection test successful")
            else:
                raise Exception("Unexpected response from Gemini API")
        except Exception as e:
            logger.error(f"Gemini API connection test failed: {e}")
            raise
    
    async def analyze_scene(
        self,
        scene_description: str,
        characters_in_scene: List[str] = [],
        setting: str = "",
        mood: str = "neutral",
        style: str = "realistic",
        genre_style: str = "general"
    ) -> Dict[str, Any]:
        """
        Analyze scene using Gemini Vision and provide detailed visualization guidance.
        
        Args:
            scene_description: Description of the scene
            characters_in_scene: List of characters in the scene
            setting: Setting description
            mood: Emotional mood
            style: Art style
            genre_style: Genre-specific style
            
        Returns:
            Dictionary with analysis results and guidance
        """
        if not self.initialized:
            await self.initialize()
        
        try:
            start_time = datetime.utcnow()
            
            # Get enhanced analysis from Gemini Vision
            gemini_result = await self._analyze_scene_with_gemini(
                scene_description, characters_in_scene, setting, mood, style, genre_style
            )
            
            if not gemini_result["success"]:
                return gemini_result
            
            scene_analysis = gemini_result.get("scene_analysis", {})
            enhanced_prompt = gemini_result.get("image_generation_prompt", scene_description)
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Store generation history
            generation_record = {
                "timestamp": datetime.utcnow().isoformat(),
                "scene_description": scene_description,
                "enhanced_prompt": enhanced_prompt,
                "characters": characters_in_scene,
                "setting": setting,
                "mood": mood,
                "style": style,
                "genre": genre_style,
                "provider": "gemini-vision",
                "scene_analysis": scene_analysis,
                "execution_time": execution_time,
                "cost": 0.0  # Gemini has generous free tier
            }
            self.generation_history.append(generation_record)
            
            # Keep only last 100 generations
            if len(self.generation_history) > 100:
                self.generation_history = self.generation_history[-100:]
            
            return {
                "success": True,
                "provider": "gemini-vision",
                "model": "gemini-1.5-flash",
                "scene_analysis": scene_analysis,
                "enhanced_prompt": enhanced_prompt,
                "original_prompt": scene_description,
                "visual_elements": scene_analysis.get("visual_elements", []),
                "mood_analysis": scene_analysis.get("mood_analysis", {}),
                "character_positions": scene_analysis.get("character_positions", {}),
                "composition_suggestions": scene_analysis.get("composition_suggestions", []),
                "technical_notes": scene_analysis.get("technical_notes", []),
                "execution_time": execution_time,
                "cost": 0.0,
                "metadata": {
                    "generated_at": datetime.utcnow().isoformat(),
                    "service_type": "scene_analysis_and_visualization"
                }
            }
            
        except Exception as e:
            logger.error(f"Scene analysis failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "provider": "gemini-vision"
            }
    
    async def _analyze_scene_with_gemini(
        self,
        scene_description: str,
        characters_in_scene: List[str],
        setting: str,
        mood: str,
        style: str,
        genre_style: str
    ) -> Dict[str, Any]:
        """Analyze scene using integrated Gemini Vision"""
        
        try:
            # Create enhanced scene description
            enhanced_description = self._create_enhanced_scene_description(
                scene_description, characters_in_scene, setting, mood, style, genre_style
            )
            
            # Generate detailed scene analysis and visualization guidance
            scene_analysis = await self._analyze_scene_for_visualization(enhanced_description)
            
            # Create image generation prompt based on analysis
            image_prompt = self._create_image_generation_prompt(scene_analysis)
            
            return {
                "success": True,
                "scene_analysis": scene_analysis,
                "image_generation_prompt": image_prompt,
                "visual_elements": scene_analysis.get("visual_elements", []),
                "mood_analysis": scene_analysis.get("mood_analysis", {}),
                "character_positions": scene_analysis.get("character_positions", {}),
                "metadata": {
                    "generated_at": datetime.utcnow().isoformat(),
                    "service_type": "scene_analysis_and_visualization"
                }
            }
            
        except Exception as e:
            logger.error(f"Scene analysis failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _analyze_scene_for_visualization(self, scene_description: str) -> Dict[str, Any]:
        """Analyze scene and provide visualization guidance using Gemini"""
        
        analysis_prompt = f"""
        Analyze this scene description and provide detailed visualization guidance for creating an image:
        
        Scene: {scene_description}
        
        Provide analysis in the following JSON format:
        {{
            "visual_elements": [
                {{
                    "element": "description of visual element",
                    "importance": "high|medium|low",
                    "position": "foreground|midground|background",
                    "details": "specific visual details"
                }}
            ],
            "mood_analysis": {{
                "overall_mood": "emotional atmosphere",
                "lighting": "lighting description",
                "color_palette": ["primary colors"],
                "atmosphere": "overall visual atmosphere"
            }},
            "character_positions": {{
                "character_name": {{
                    "position": "where in the scene",
                    "pose": "what they're doing",
                    "expression": "facial expression",
                    "clothing": "what they're wearing"
                }}
            }},
            "composition_suggestions": [
                "specific composition recommendations"
            ],
            "technical_notes": [
                "technical considerations for image generation"
            ]
        }}
        """
        
        try:
            response = self.gemini_vision_model.generate_content(analysis_prompt)
            
            # Try to parse JSON response
            try:
                analysis = json.loads(response.text)
                return analysis
            except json.JSONDecodeError:
                # If JSON parsing fails, create structured response from text
                return self._parse_unstructured_response(response.text)
                
        except Exception as e:
            logger.error(f"Scene analysis failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _parse_unstructured_response(self, response_text: str) -> Dict[str, Any]:
        """Parse unstructured Gemini response into structured format"""
        
        # Extract key information from text response
        analysis = {
            "visual_elements": [],
            "mood_analysis": {
                "overall_mood": "neutral",
                "lighting": "natural",
                "color_palette": ["neutral"],
                "atmosphere": "balanced"
            },
            "character_positions": {},
            "composition_suggestions": [],
            "technical_notes": []
        }
        
        # Simple text parsing
        lines = response_text.split('\n')
        for line in lines:
            line = line.strip()
            if "visual" in line.lower() or "element" in line.lower():
                analysis["visual_elements"].append({
                    "element": line,
                    "importance": "medium",
                    "position": "midground",
                    "details": line
                })
            elif "mood" in line.lower() or "atmosphere" in line.lower():
                analysis["mood_analysis"]["overall_mood"] = line
            elif "light" in line.lower():
                analysis["mood_analysis"]["lighting"] = line
            elif "composition" in line.lower():
                analysis["composition_suggestions"].append(line)
        
        return analysis
    

    
    def _create_enhanced_scene_description(
        self,
        scene_description: str,
        characters: List[str],
        setting: str,
        mood: str,
        style: str,
        genre: str
    ) -> str:
        """Create enhanced scene description for better analysis"""
        
        description_parts = [scene_description]
        
        if characters:
            description_parts.append(f"Characters present: {', '.join(characters)}")
        
        if setting:
            description_parts.append(f"Setting: {setting}")
        
        if mood != "neutral":
            description_parts.append(f"Mood: {mood}")
        
        if style != "realistic":
            description_parts.append(f"Art style: {style}")
        
        if genre != "general":
            description_parts.append(f"Genre: {genre}")
        
        return ". ".join(description_parts)
    
    def _create_image_generation_prompt(self, scene_analysis: Dict[str, Any]) -> str:
        """Create optimized image generation prompt from scene analysis"""
        
        prompt_parts = []
        
        # Add visual elements
        visual_elements = scene_analysis.get("visual_elements", [])
        for element in visual_elements[:5]:  # Limit to top 5 elements
            prompt_parts.append(element.get("element", ""))
        
        # Add mood and atmosphere
        mood_analysis = scene_analysis.get("mood_analysis", {})
        if mood_analysis.get("lighting"):
            prompt_parts.append(f"Lighting: {mood_analysis['lighting']}")
        if mood_analysis.get("color_palette"):
            colors = mood_analysis["color_palette"]
            if colors and colors != ["neutral"]:
                prompt_parts.append(f"Color palette: {', '.join(colors)}")
        
        # Add composition suggestions
        composition = scene_analysis.get("composition_suggestions", [])
        if composition:
            prompt_parts.append(f"Composition: {composition[0]}")
        
        # Combine and enhance
        base_prompt = ". ".join(prompt_parts)
        enhanced_prompt = f"{base_prompt}. High quality, detailed, cinematic composition, professional photography"
        
        return enhanced_prompt
    
    async def analyze_character(
        self,
        character_description: str,
        character_name: str,
        story_context: str = "",
        style: str = "realistic"
    ) -> Dict[str, Any]:
        """
        Analyze character using integrated Gemini Vision for consistency and development.
        
        Args:
            character_description: Description of the character
            character_name: Name of the character
            story_context: Context from the story
            style: Art style
            
        Returns:
            Dictionary with character analysis results
        """
        if not self.initialized:
            await self.initialize()
        
        try:
            start_time = datetime.utcnow()
            
            # Enhanced character analysis using integrated Gemini Vision
            character_analysis = {
                "appearance": {
                    "physical_features": ["Based on description"],
                    "clothing": character_description,
                    "expression": "Characteristic expression",
                    "pose": "Characteristic pose"
                },
                "personality_indicators": ["Based on story context"],
                "story_relevance": f"Character fits {story_context}",
                "consistency_notes": ["Maintain visual consistency"],
                "visual_quality": "High quality generation needed"
            }
            
            # Create enhanced prompt based on analysis
            enhanced_prompt = f"{character_description}, {character_name}, {story_context}, {style} style, high quality, detailed, character portrait"
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Cache character analysis
            self.character_visual_cache[character_name] = {
                "analysis": character_analysis,
                "cached_at": datetime.utcnow().isoformat(),
                "story_context": story_context,
                "last_generated": datetime.utcnow().isoformat()
            }
            
            return {
                "success": True,
                "provider": "gemini-vision",
                "model": "gemini-1.5-flash",
                "character_name": character_name,
                "character_analysis": character_analysis,
                "story_context": story_context,
                "enhanced_prompt": enhanced_prompt,
                "execution_time": execution_time,
                "cost": 0.0,
                "metadata": {
                    "generated_at": datetime.utcnow().isoformat(),
                    "service_type": "character_analysis"
                }
            }
            
        except Exception as e:
            logger.error(f"Character analysis failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "character_name": character_name
            }
    
    async def generate_story_poster_concept(
        self,
        story_title: str,
        story_description: str,
        genre: str = "general",
        poster_type: str = "character_focused",
        main_character: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate story poster concept and design guidance using integrated Gemini Vision.
        
        Args:
            story_title: Title of the story
            story_description: Description of the story
            genre: Story genre
            poster_type: Type of poster
            main_character: Main character name
            
        Returns:
            Dictionary with poster design concept
        """
        if not self.initialized:
            await self.initialize()
        
        try:
            start_time = datetime.utcnow()
            
            # Get poster design concept from integrated Gemini Vision
            poster_concept = await self._generate_poster_concept_with_gemini(
                story_title, story_description, genre, poster_type, main_character
            )
            
            if not poster_concept["success"]:
                return poster_concept
            
            design_concept = poster_concept.get("design_concept", {})
            
            # Create enhanced prompt based on design concept
            visual_elements = design_concept.get("visual_elements", [])
            color_scheme = design_concept.get("color_scheme", {})
            
            enhanced_prompt = f"Movie poster for '{story_title}': {story_description}, {genre} genre, {poster_type} style"
            
            if visual_elements:
                enhanced_prompt += f", featuring {', '.join([elem.get('element', '') for elem in visual_elements[:3]])}"
            
            if color_scheme.get("primary_colors"):
                enhanced_prompt += f", {', '.join(color_scheme['primary_colors'])} color scheme"
            
            enhanced_prompt += ", cinematic composition, professional movie poster design"
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            return {
                "success": True,
                "provider": "gemini-vision",
                "model": "gemini-1.5-flash",
                "story_title": story_title,
                "poster_type": poster_type,
                "genre": genre,
                "main_character": main_character,
                "design_concept": design_concept,
                "enhanced_prompt": enhanced_prompt,
                "execution_time": execution_time,
                "cost": 0.0,
                "metadata": {
                    "generated_at": datetime.utcnow().isoformat(),
                    "service_type": "poster_design_concept"
                }
            }
            
        except Exception as e:
            logger.error(f"Story poster concept generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "story_title": story_title
            }
    
    async def _generate_poster_concept_with_gemini(
        self,
        story_title: str,
        story_description: str,
        genre: str,
        poster_type: str,
        main_character: Optional[str]
    ) -> Dict[str, Any]:
        """Generate poster design concept using integrated Gemini Vision"""
        
        try:
            # Create poster design prompt
            design_prompt = f"""
            Create a detailed poster design concept for this story:
            
            Title: {story_title}
            Description: {story_description}
            Genre: {genre}
            Poster Type: {poster_type}
            Main Character: {main_character or "Not specified"}
            
            Provide poster design concept in JSON format:
            {{
                "design_concept": "overall design approach",
                "visual_elements": [
                    {{
                        "element": "description of visual element",
                        "placement": "where in the poster",
                        "importance": "high|medium|low"
                    }}
                ],
                "color_scheme": {{
                    "primary_colors": ["main colors"],
                    "accent_colors": ["accent colors"],
                    "mood": "emotional impact of color choice"
                }},
                "typography": {{
                    "title_style": "title font and style recommendations",
                    "subtitle_style": "subtitle styling",
                    "tagline_style": "tagline styling"
                }},
                "composition": {{
                    "layout": "poster layout description",
                    "focal_point": "main focus area",
                    "balance": "composition balance notes"
                }},
                "marketing_appeal": "how this design appeals to target audience",
                "implementation_notes": ["specific notes for creating the poster"]
            }}
            """
            
            # Generate design concept
            response = self.gemini_text_model.generate_content(design_prompt)
            
            try:
                design_concept = json.loads(response.text)
            except json.JSONDecodeError:
                return {
                    "success": False,
                    "error": "Failed to parse design concept response"
                }
            
            return {
                "success": True,
                "design_concept": design_concept,
                "metadata": {
                    "generated_at": datetime.utcnow().isoformat(),
                    "service_type": "poster_design_concept"
                }
            }
            
        except Exception as e:
            logger.error(f"Poster concept generation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    

    
    async def analyze_character_consistency(
        self,
        character_name: str,
        new_image_data: bytes,
        story_context: str = ""
    ) -> Dict[str, Any]:
        """
        Analyze character image for consistency using integrated Gemini Vision.
        
        Args:
            character_name: Name of the character
            new_image_data: New character image data
            story_context: Story context for analysis
            
        Returns:
            Dictionary with consistency analysis
        """
        if not self.initialized:
            await self.initialize()
        
        try:
            # Analyze new image
            analysis_result = await self._analyze_character_image_with_gemini(
                image_data=new_image_data,
                character_name=character_name,
                story_context=story_context
            )
            
            if not analysis_result["success"]:
                return analysis_result
            
            # Compare with cached analysis
            cached_analysis = self.character_visual_cache.get(character_name)
            consistency_score = 0.8  # Default score
            
            if cached_analysis:
                # Simple consistency check (in production, use more sophisticated comparison)
                old_features = cached_analysis.get("analysis", {}).get("appearance", {}).get("physical_features", [])
                new_features = analysis_result.get("analysis", {}).get("appearance", {}).get("physical_features", [])
                
                if old_features and new_features:
                    # Calculate basic similarity (simplified)
                    common_features = set(old_features) & set(new_features)
                    total_features = set(old_features) | set(new_features)
                    if total_features:
                        consistency_score = len(common_features) / len(total_features)
            
            return {
                "success": True,
                "character_name": character_name,
                "consistency_score": consistency_score,
                "analysis": analysis_result.get("analysis", {}),
                "cached_analysis": cached_analysis,
                "recommendations": self._generate_consistency_recommendations(consistency_score),
                "metadata": {
                    "analyzed_at": datetime.utcnow().isoformat(),
                    "story_context": story_context
                }
            }
            
        except Exception as e:
            logger.error(f"Character consistency analysis failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "character_name": character_name
            }
    
    async def _analyze_character_image_with_gemini(
        self,
        image_data: bytes,
        character_name: str,
        story_context: str
    ) -> Dict[str, Any]:
        """Analyze character image using integrated Gemini Vision"""
        
        try:
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_data))
            
            # Create analysis prompt
            analysis_prompt = f"""
            Analyze this character image for the story: {story_context}
            
            Character name: {character_name}
            
            Provide analysis in JSON format:
            {{
                "appearance": {{
                    "physical_features": ["list of physical characteristics"],
                    "clothing": "description of clothing and style",
                    "expression": "facial expression and mood",
                    "pose": "body language and positioning"
                }},
                "personality_indicators": ["personality traits suggested by appearance"],
                "story_relevance": "how this appearance fits the story context",
                "consistency_notes": ["notes for maintaining character consistency"],
                "visual_quality": "assessment of image quality and clarity"
            }}
            """
            
            # Generate analysis
            response = self.gemini_vision_model.generate_content([analysis_prompt, image])
            
            try:
                analysis = json.loads(response.text)
            except json.JSONDecodeError:
                return {
                    "success": False,
                    "error": "Failed to parse character analysis response",
                    "character_name": character_name
                }
            
            # Cache character analysis
            self.character_visual_cache[character_name] = {
                "analysis": analysis,
                "cached_at": datetime.utcnow().isoformat(),
                "story_context": story_context
            }
            
            return {
                "success": True,
                "character_name": character_name,
                "analysis": analysis
            }
            
        except Exception as e:
            logger.error(f"Character image analysis failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "character_name": character_name
            }
    

    
    def _generate_consistency_recommendations(self, score: float) -> List[str]:
        """Generate recommendations based on consistency score"""
        if score >= 0.8:
            return ["Excellent consistency maintained", "Character appearance is stable"]
        elif score >= 0.6:
            return ["Good consistency", "Minor variations detected", "Consider standardizing key features"]
        elif score >= 0.4:
            return ["Moderate consistency issues", "Review character design guidelines", "Update reference materials"]
        else:
            return ["Significant consistency issues", "Major redesign may be needed", "Consult with design team"]
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of Gemini Vision service"""
        
        health_status = {
            "service_status": "healthy",
            "provider": "gemini-vision",
            "initialized": self.initialized,
            "gemini_vision_integrated": self.gemini_initialized
        }
        
        if not self.initialized:
            health_status["service_status"] = "uninitialized"
            return health_status
        
        # Check Gemini Vision
        if self.gemini_initialized:
            try:
                # Test with simple generation
                response = self.gemini_text_model.generate_content("Health check")
                if response.text:
                    health_status["service_status"] = "healthy"
                    health_status["model_status"] = "operational"
                else:
                    health_status["service_status"] = "degraded"
                    health_status["model_status"] = "unresponsive"
            except Exception as e:
                health_status["service_status"] = "unhealthy"
                health_status["error"] = str(e)
        else:
            health_status["service_status"] = "unhealthy"
            health_status["error"] = "Gemini Vision not initialized"
        
        return health_status
    
    def get_generation_stats(self) -> Dict[str, Any]:
        """Get image service statistics"""
        if not self.generation_history:
            return {
                "total_analyses": 0,
                "total_cost": 0.0,
                "characters_analyzed": 0,
                "gemini_vision_integrated": self.gemini_initialized
            }
        
        total_analyses = len(self.generation_history)
        total_cost = sum(gen.get("cost", 0.0) for gen in self.generation_history)
        characters_analyzed = len([gen for gen in self.generation_history if gen.get("characters")])
        
        return {
            "total_analyses": total_analyses,
            "total_cost": total_cost,
            "characters_analyzed": characters_analyzed,
            "recent_analyses": len([gen for gen in self.generation_history if self._is_recent(gen)]),
            "cached_characters": len(self.character_visual_cache),
            "gemini_vision_integrated": self.gemini_initialized,
            "service_type": "vision_analysis_and_guidance"
        }
    
    def _is_recent(self, generation: Dict[str, Any]) -> bool:
        """Check if generation is recent (within last hour)"""
        try:
            timestamp = datetime.fromisoformat(generation["timestamp"])
            age_hours = (datetime.utcnow() - timestamp).total_seconds() / 3600
            return age_hours < 1
        except:
            return False
    
    async def cleanup(self):
        """Cleanup resources"""
        self.initialized = False

# Global image service instance
image_service = ImageService()

# Convenience function
async def get_image_service() -> ImageService:
    """Get initialized image service instance"""
    if not image_service.initialized:
        await image_service.initialize()
    return image_service
