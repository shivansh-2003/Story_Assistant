# agents/narrative_intelligence.py
from typing import Dict, Any, List, Optional
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
import json
import logging
import re

from .base_agent import BaseAgent
from models.generation_models import (
    AgentContext, AgentType, StoryContext,
    ContentGenerationContext
)
from services.vector_service import VectorService

logger = logging.getLogger(__name__)

class NarrativeIntelligenceAgent(BaseAgent):
    """
    Narrative Intelligence Agent
    
    Responsibilities:
    - Chapter-to-chapter transition seamless bridging
    - Character arc progression across unlimited chapter content
    - Plot thread weaving with memory of all previous content
    - Dynamic story expansion based on user mid-flow inputs
    - Incremental content generation with perfect context retention
    - Story momentum and pacing across variable chapter lengths
    - Character voice consistency and dialogue generation
    - Narrative flow and storytelling techniques
    """
    
    def __init__(self, vector_service: VectorService):
        super().__init__(
            agent_type=AgentType.NARRATIVE_INTELLIGENCE,
            vector_service=vector_service
        )
        self.character_voice_patterns: Dict[str, Dict[str, Any]] = {}
        self.plot_thread_tracker: Dict[str, Dict[str, Any]] = {}
    
    def _get_agent_role_description(self) -> str:
        return """
        As the Narrative Intelligence Agent, you are the master storyteller responsible for 
        generating compelling, coherent narrative content that maintains character consistency,
        advances plot threads, and creates engaging reading experiences.
        
        Your key responsibilities:
        1. Generate high-quality narrative content with proper pacing and flow
        2. Maintain consistent character voices and personalities across all content
        3. Weave multiple plot threads together seamlessly
        4. Create smooth transitions between chapters and story segments
        5. Adapt writing style to match genre, audience, and user preferences
        6. Ensure narrative momentum and reader engagement
        7. Handle character development and relationship dynamics
        8. Create authentic dialogue that reflects character personalities
        """
    
    async def _execute_task(self, context: AgentContext) -> Dict[str, Any]:
        """
        Execute Narrative Intelligence specific tasks
        """
        task_data = context.agent_specific_data
        task_type = task_data.get("task_type", "generate_content")
        
        if task_type == "generate_content":
            return await self._generate_story_content(context)
        elif task_type == "generate_dialogue":
            return await self._generate_dialogue(context)
        elif task_type == "continue_chapter":
            return await self._continue_chapter(context)
        elif task_type == "bridge_chapters":
            return await self._bridge_chapters(context)
        elif task_type == "develop_character_arc":
            return await self._develop_character_arc(context)
        elif task_type == "advance_plot":
            return await self._advance_plot_threads(context)
        else:
            raise ValueError(f"Unknown task type: {task_type}")
    
    async def _generate_story_content(self, context: AgentContext) -> Dict[str, Any]:
        """
        Main content generation method
        """
        logger.info(f"Generating story content for task {context.task_id}")
        
        # 1. Analyze generation requirements
        generation_context = await self._analyze_generation_requirements(context)
        
        # 2. Gather relevant story context
        story_context = await self._gather_narrative_context(context)
        
        # 3. Plan content structure
        content_plan = await self._plan_content_structure(context, generation_context, story_context)
        
        # 4. Generate content segments
        content_segments = await self._generate_content_segments(context, content_plan, story_context)
        
        # 5. Assemble and refine content
        final_content = await self._assemble_content(context, content_segments, content_plan)
        
        # 6. Store context for future use
        await self._store_generation_context(context, final_content, story_context)
        
        return {
            "content": final_content["text"],
            "word_count": final_content["word_count"],
            "character_consistency_scores": final_content.get("character_scores", {}),
            "plot_advancement": final_content.get("plot_advancement", {}),
            "generation_metadata": {
                "generation_context": generation_context,
                "content_plan": content_plan,
                "segments_generated": len(content_segments)
            },
            "continuation_hooks": final_content.get("continuation_hooks", []),
            "character_developments": final_content.get("character_developments", {})
        }
    
    async def _analyze_generation_requirements(self, context: AgentContext) -> Dict[str, Any]:
        """
        Analyze what kind of content needs to be generated
        """
        user_input = context.user_input or ""
        story_context = context.story_context
        task_data = context.agent_specific_data
        
        analysis_prompt = """
        Analyze the generation requirements for this story content:
        
        User Input: "{user_input}"
        
        Story Context:
        - Genre: {genre}
        - Writing Style: {writing_style}
        - Target Audience: {target_audience}
        - Current Chapter: {current_chapter}
        - Target Word Count: {target_words}
        
        Previous Context: {previous_context}
        
        Determine the content requirements in JSON format:
        {{
            "content_type": "narrative|dialogue|description|action|mixed",
            "primary_focus": "plot_advancement|character_development|world_building|atmosphere",
            "narrative_perspective": "first_person|third_person_limited|third_person_omniscient",
            "tense": "past|present|mixed",
            "tone": "serious|light|dramatic|humorous|dark|adventurous",
            "pacing": "slow|moderate|fast|varied",
            "characters_involved": ["list of character names/IDs mentioned"],
            "setting_requirements": "location and time details needed",
            "plot_elements": ["specific plot points to address"],
            "emotional_beats": ["emotional moments to include"],
            "dialogue_ratio": "high|medium|low",
            "descriptive_detail_level": "minimal|moderate|rich|lavish"
        }}
        """
        
        context_vars = {
            "user_input": user_input,
            "genre": story_context.story_metadata.get("genre", "Unknown"),
            "writing_style": story_context.story_metadata.get("writing_style", "balanced"),
            "target_audience": story_context.story_metadata.get("target_audience", "adult"),
            "current_chapter": story_context.current_chapter_id or "New story",
            "target_words": task_data.get("target_word_count", 250),
            "previous_context": story_context.previous_content[-500:] if story_context.previous_content else "No previous content"
        }
        
        result = await self._generate_with_llm(
            analysis_prompt,
            context_vars,
            JsonOutputParser()
        )
        
        return result
    
    async def _gather_narrative_context(self, context: AgentContext) -> Dict[str, Any]:
        """
        Gather all relevant context for narrative generation
        """
        story_context = context.story_context
        user_input = context.user_input or ""
        
        # Create search query for relevant context
        search_terms = []
        if user_input:
            search_terms.append(user_input)
        search_terms.extend([
            story_context.story_metadata.get("genre", ""),
            "narrative content"
        ])
        search_query = " ".join(search_terms)
        
        narrative_context = {}
        
        # Get character context and voice patterns
        if story_context.characters:
            character_context = await self._get_relevant_context(
                story_context, search_query, "character", max_results=5
            )
            narrative_context["characters"] = character_context
            
            # Load character voice patterns
            for char in story_context.characters:
                char_id = str(char.get("id", ""))
                if char_id not in self.character_voice_patterns:
                    await self._learn_character_voice(char_id, story_context)
        
        # Get plot context
        plot_context = await self._get_relevant_context(
            story_context, search_query, "plot", max_results=7
        )
        narrative_context["plot_threads"] = plot_context
        
        # Get dialogue patterns
        dialogue_context = await self._get_relevant_context(
            story_context, search_query, "dialogue", max_results=5
        )
        narrative_context["dialogue_patterns"] = dialogue_context
        
        # Get recent story context
        if story_context.previous_content:
            narrative_context["recent_content"] = {
                "last_1000_chars": story_context.previous_content[-1000:],
                "last_paragraph": self._extract_last_paragraph(story_context.previous_content)
            }
        
        # Get continuation context
        narrative_context["continuation_context"] = story_context.continuation_context
        
        return narrative_context
    
    async def _plan_content_structure(
        self, 
        context: AgentContext, 
        generation_context: Dict[str, Any],
        story_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Plan the structure of the content to be generated
        """
        planning_prompt = """
        Plan the structure for the story content based on requirements and context:
        
        Generation Requirements: {generation_requirements}
        
        Available Context:
        - Characters: {character_count} characters available
        - Plot Threads: {plot_thread_count} active threads
        - Previous Content: {has_previous_content}
        
        Target Word Count: {target_words}
        User Direction: {user_input}
        
        Create a content structure plan in JSON format:
        {{
            "content_segments": [
                {{
                    "segment_type": "opening|dialogue|action|description|transition|climax|resolution",
                    "word_target": "estimated words for this segment",
                    "primary_purpose": "what this segment accomplishes",
                    "characters_featured": ["characters in this segment"],
                    "plot_elements": ["plot points advanced"],
                    "emotional_tone": "emotional direction",
                    "transition_notes": "how this connects to next segment"
                }}
            ],
            "overall_arc": "the narrative arc of this content",
            "character_development_opportunities": ["chances for character growth"],
            "plot_advancement_strategy": "how plot moves forward",
            "pacing_strategy": "how to manage reading pace",
            "hook_elements": ["elements to keep reader engaged"],
            "continuation_setup": "how this sets up future content"
        }}
        """
        
        context_vars = {
            "generation_requirements": json.dumps(generation_context, indent=2),
            "character_count": len(story_context.get("characters", [])),
            "plot_thread_count": len(story_context.get("plot_threads", [])),
            "has_previous_content": "Yes" if story_context.get("recent_content") else "No",
            "target_words": context.agent_specific_data.get("target_word_count", 250),
            "user_input": context.user_input or "Continue story naturally"
        }
        
        result = await self._generate_with_llm(
            planning_prompt,
            context_vars,
            JsonOutputParser()
        )
        
        return result
    
    async def _generate_content_segments(
        self,
        context: AgentContext,
        content_plan: Dict[str, Any],
        story_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate individual content segments according to the plan
        """
        segments = []
        content_segments = content_plan.get("content_segments", [])
        
        for i, segment_plan in enumerate(content_segments):
            segment_content = await self._generate_single_segment(
                context, segment_plan, story_context, segments
            )
            segments.append(segment_content)
        
        return segments
    
    async def _generate_single_segment(
        self,
        context: AgentContext,
        segment_plan: Dict[str, Any],
        story_context: Dict[str, Any],
        previous_segments: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate a single content segment
        """
        segment_type = segment_plan.get("segment_type", "narrative")
        word_target = segment_plan.get("word_target", 50)
        
        # Build context for this segment
        segment_context = self._build_segment_context(
            context, segment_plan, story_context, previous_segments
        )
        
        if segment_type == "dialogue":
            return await self._generate_dialogue_segment(segment_plan, segment_context)
        elif segment_type == "action":
            return await self._generate_action_segment(segment_plan, segment_context)
        elif segment_type == "description":
            return await self._generate_description_segment(segment_plan, segment_context)
        else:
            return await self._generate_narrative_segment(segment_plan, segment_context)
    
    async def _generate_narrative_segment(
        self, 
        segment_plan: Dict[str, Any], 
        segment_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate a general narrative segment
        """
        narrative_prompt = """
        Write a compelling narrative segment based on the following requirements:
        
        Segment Plan: {segment_plan}
        
        Story Context: {story_context}
        
        Character Information: {character_info}
        
        Previous Content: {previous_content}
        
        Requirements:
        - Write approximately {word_target} words
        - Maintain the {tone} tone
        - Focus on {primary_purpose}
        - Include characters: {characters}
        - Advance these plot elements: {plot_elements}
        - Use {narrative_perspective} perspective
        
        Write engaging, well-paced narrative content that flows naturally from any previous content.
        Ensure character voices are consistent and dialogue feels authentic.
        Create vivid scenes that immerse the reader while advancing the story.
        """
        
        context_vars = {
            "segment_plan": json.dumps(segment_plan, indent=2),
            "story_context": json.dumps(segment_context.get("story_metadata", {})),
            "character_info": json.dumps(segment_context.get("character_info", {})),
            "previous_content": segment_context.get("previous_content", ""),
            "word_target": segment_plan.get("word_target", 100),
            "tone": segment_plan.get("emotional_tone", "balanced"),
            "primary_purpose": segment_plan.get("primary_purpose", "advance story"),
            "characters": ", ".join(segment_plan.get("characters_featured", [])),
            "plot_elements": ", ".join(segment_plan.get("plot_elements", [])),
            "narrative_perspective": segment_context.get("perspective", "third person")
        }
        
        content = await self._generate_with_llm(
            narrative_prompt,
            context_vars,
            StrOutputParser()
        )
        
        return {
            "content": content,
            "segment_type": "narrative",
            "word_count": len(content.split()),
            "characters_featured": segment_plan.get("characters_featured", []),
            "plot_advancement": segment_plan.get("plot_elements", [])
        }
    
    async def _generate_dialogue_segment(
        self, 
        segment_plan: Dict[str, Any], 
        segment_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate dialogue-focused segment with character voice consistency
        """
        characters = segment_plan.get("characters_featured", [])
        character_voices = {}
        
        # Get character voice patterns
        for char_id in characters:
            if char_id in self.character_voice_patterns:
                character_voices[char_id] = self.character_voice_patterns[char_id]
        
        dialogue_prompt = """
        Write a dialogue-heavy segment with authentic character voices:
        
        Characters in Scene: {characters}
        Character Voice Patterns: {character_voices}
        
        Scene Context: {scene_context}
        Emotional Tone: {emotional_tone}
        Purpose: {purpose}
        
        Target Length: {word_target} words
        
        Guidelines:
        - Each character should speak in their unique voice and style
        - Dialogue should feel natural and serve the story purpose
        - Include appropriate dialogue tags and action beats
        - Show character emotions through their speech patterns
        - Advance the plot through conversation
        - Maintain proper dialogue formatting
        
        Write compelling dialogue that reveals character and advances the story.
        """
        
        context_vars = {
            "characters": ", ".join(characters),
            "character_voices": json.dumps(character_voices, indent=2),
            "scene_context": json.dumps(segment_context.get("scene_info", {})),
            "emotional_tone": segment_plan.get("emotional_tone", "conversational"),
            "purpose": segment_plan.get("primary_purpose", "character interaction"),
            "word_target": segment_plan.get("word_target", 150)
        }
        
        content = await self._generate_with_llm(
            dialogue_prompt,
            context_vars,
            StrOutputParser()
        )
        
        return {
            "content": content,
            "segment_type": "dialogue",
            "word_count": len(content.split()),
            "characters_featured": characters,
            "dialogue_ratio": "high"
        }
    
    async def _generate_action_segment(
        self, 
        segment_plan: Dict[str, Any], 
        segment_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate action-focused segment with dynamic pacing
        """
        action_prompt = """
        Write a dynamic action sequence with strong pacing and vivid imagery:
        
        Action Context: {action_context}
        Characters Involved: {characters}
        Setting: {setting}
        
        Requirements:
        - Approximately {word_target} words
        - Fast-paced, engaging action
        - Clear, vivid descriptions of events
        - Character reactions and emotions during action
        - Sensory details that immerse the reader
        - Appropriate tension and stakes
        
        Purpose: {purpose}
        Tone: {tone}
        
        Write compelling action that keeps readers on the edge of their seats.
        Use short, punchy sentences for intensity and longer ones for description.
        Show don't tell - let actions reveal character and advance plot.
        """
        
        context_vars = {
            "action_context": json.dumps(segment_context.get("action_info", {})),
            "characters": ", ".join(segment_plan.get("characters_featured", [])),
            "setting": segment_context.get("setting", "current location"),
            "word_target": segment_plan.get("word_target", 120),
            "purpose": segment_plan.get("primary_purpose", "create excitement"),
            "tone": segment_plan.get("emotional_tone", "intense")
        }
        
        content = await self._generate_with_llm(
            action_prompt,
            context_vars,
            StrOutputParser()
        )
        
        return {
            "content": content,
            "segment_type": "action",
            "word_count": len(content.split()),
            "pacing": "fast",
            "intensity": "high"
        }
    
    async def _generate_description_segment(
        self, 
        segment_plan: Dict[str, Any], 
        segment_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate descriptive segment focusing on setting, atmosphere, or character
        """
        description_prompt = """
        Write rich, immersive description that enhances the story atmosphere:
        
        Description Focus: {focus}
        Setting Details: {setting}
        Mood/Atmosphere: {mood}
        
        Requirements:
        - Approximately {word_target} words
        - Vivid, sensory-rich descriptions
        - Show the environment/character through specific details
        - Create appropriate mood and atmosphere
        - Use varied sentence structure for flow
        - Avoid purple prose - keep descriptions purposeful
        
        Purpose: {purpose}
        Style: {style}
        
        Write description that immerses readers and enhances the story experience.
        Use the five senses and specific, concrete details rather than abstract concepts.
        """
        
        context_vars = {
            "focus": segment_plan.get("primary_purpose", "setting description"),
            "setting": segment_context.get("setting", "current scene"),
            "mood": segment_plan.get("emotional_tone", "atmospheric"),
            "word_target": segment_plan.get("word_target", 100),
            "purpose": segment_plan.get("primary_purpose", "establish atmosphere"),
            "style": segment_context.get("writing_style", "descriptive")
        }
        
        content = await self._generate_with_llm(
            description_prompt,
            context_vars,
            StrOutputParser()
        )
        
        return {
            "content": content,
            "segment_type": "description",
            "word_count": len(content.split()),
            "descriptive_focus": segment_plan.get("primary_purpose", "setting")
        }
    
    def _build_segment_context(
        self,
        context: AgentContext,
        segment_plan: Dict[str, Any],
        story_context: Dict[str, Any],
        previous_segments: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Build context specific to this segment
        """
        segment_context = {
            "story_metadata": context.story_context.story_metadata,
            "generation_settings": context.story_context.generation_settings,
            "perspective": context.story_context.story_metadata.get("perspective", "third_person"),
            "writing_style": context.story_context.story_metadata.get("writing_style", "balanced")
        }
        
        # Add character information for featured characters
        characters_featured = segment_plan.get("characters_featured", [])
        if characters_featured:
            character_info = {}
            for char_id in characters_featured:
                # Get character info from story context
                for char in context.story_context.characters:
                    if str(char.get("id", "")) == char_id or char.get("name", "") == char_id:
                        character_info[char_id] = char
                        break
            segment_context["character_info"] = character_info
        
        # Add previous content context
        if previous_segments:
            recent_content = " ".join([seg.get("content", "") for seg in previous_segments[-2:]])
            segment_context["previous_content"] = recent_content
        elif story_context.get("recent_content"):
            segment_context["previous_content"] = story_context["recent_content"]["last_paragraph"]
        
        return segment_context
    
    async def _assemble_content(
        self,
        context: AgentContext,
        content_segments: List[Dict[str, Any]],
        content_plan: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Assemble final content from segments with transitions and polish
        """
        if not content_segments:
            return {"text": "", "word_count": 0}
        
        # Combine segment content
        combined_content = []
        total_word_count = 0
        character_appearances = {}
        plot_advancements = []
        
        for i, segment in enumerate(content_segments):
            content = segment.get("content", "")
            combined_content.append(content)
            total_word_count += segment.get("word_count", 0)
            
            # Track character appearances
            for char in segment.get("characters_featured", []):
                character_appearances[char] = character_appearances.get(char, 0) + 1
            
            # Track plot advancement
            plot_advancements.extend(segment.get("plot_advancement", []))
        
        # Join segments with appropriate transitions
        final_text = await self._create_smooth_transitions(combined_content, content_plan)
        
        # Generate continuation hooks
        continuation_hooks = await self._generate_continuation_hooks(
            final_text, context, content_plan
        )
        
        return {
            "text": final_text,
            "word_count": len(final_text.split()),
            "character_scores": self._calculate_character_consistency_scores(
                final_text, character_appearances
            ),
            "plot_advancement": {
                "elements_advanced": plot_advancements,
                "advancement_score": len(plot_advancements) / max(len(content_segments), 1)
            },
            "continuation_hooks": continuation_hooks,
            "character_developments": character_appearances
        }
    
    async def _create_smooth_transitions(
        self, 
        content_segments: List[str], 
        content_plan: Dict[str, Any]
    ) -> str:
        """
        Create smooth transitions between content segments
        """
        if len(content_segments) <= 1:
            return " ".join(content_segments)
        
        # For now, use simple paragraph breaks
        # In a more sophisticated version, you could generate transition sentences
        return "\n\n".join(content_segments)
    
    async def _generate_continuation_hooks(
        self,
        content: str,
        context: AgentContext,
        content_plan: Dict[str, Any]
    ) -> List[str]:
        """
        Generate hooks for future content continuation
        """
        hook_prompt = """
        Analyze this story content and identify continuation opportunities:
        
        Content: {content_excerpt}
        
        Content Plan: {content_plan}
        
        Identify continuation hooks in JSON format:
        {{
            "plot_hooks": ["unresolved plot elements that can be developed"],
            "character_hooks": ["character development opportunities"],
            "tension_hooks": ["conflicts or tensions to explore"],
            "world_hooks": ["world-building elements to expand"],
            "mystery_hooks": ["questions or mysteries to resolve"]
        }}
        """
        
        context_vars = {
            "content_excerpt": content[-500:],  # Last 500 characters
            "content_plan": json.dumps(content_plan.get("continuation_setup", {}))
        }
        
        try:
            result = await self._generate_with_llm(
                hook_prompt,
                context_vars,
                JsonOutputParser()
            )
            
            # Flatten all hooks into a single list
            all_hooks = []
            for hook_type, hooks in result.items():
                if isinstance(hooks, list):
                    all_hooks.extend(hooks)
            
            return all_hooks
            
        except Exception as e:
            logger.warning(f"Failed to generate continuation hooks: {e}")
            return []
    
    def _calculate_character_consistency_scores(
        self, 
        content: str, 
        character_appearances: Dict[str, int]
    ) -> Dict[str, float]:
        """
        Calculate character consistency scores based on voice patterns
        """
        scores = {}
        
        for char_id, appearances in character_appearances.items():
            if char_id in self.character_voice_patterns:
                # Simple consistency check - in a real implementation,
                # you'd use more sophisticated NLP analysis
                voice_pattern = self.character_voice_patterns[char_id]
                
                # Check for character-specific phrases or patterns
                consistency_indicators = 0
                total_checks = 0
                
                for phrase in voice_pattern.get("common_phrases", []):
                    total_checks += 1
                    if phrase.lower() in content.lower():
                        consistency_indicators += 1
                
                # Calculate score
                if total_checks > 0:
                    scores[char_id] = consistency_indicators / total_checks
                else:
                    scores[char_id] = 0.8  # Default score when no patterns to check
            else:
                scores[char_id] = 0.7  # Default score for unknown characters
        
        return scores
    
    async def _learn_character_voice(self, character_id: str, story_context: StoryContext):
        """
        Learn character voice patterns from previous content
        """
        # Search for previous dialogue by this character
        dialogue_context = await self._get_relevant_context(
            story_context, f"character_{character_id} dialogue", "dialogue", max_results=10
        )
        
        if dialogue_context:
            # Analyze patterns in the dialogue
            # This is a simplified version - you'd use more sophisticated NLP
            voice_pattern = {
                "common_phrases": [],
                "vocabulary_level": "moderate",
                "sentence_length": "varied",
                "speech_quirks": []
            }
            
            self.character_voice_patterns[character_id] = voice_pattern
    
    def _extract_last_paragraph(self, content: str) -> str:
        """
        Extract the last paragraph from content
        """
        if not content:
            return ""
        
        paragraphs = content.split("\n\n")
        return paragraphs[-1] if paragraphs else content[-200:]
    
    async def _store_generation_context(
        self,
        context: AgentContext,
        final_content: Dict[str, Any],
        story_context: Dict[str, Any]
    ):
        """
        Store generation context in vector database for future reference
        """
        try:
            # Store the generated content with metadata
            await self._store_result_in_vector_db(
                content=final_content["text"],
                metadata={
                    "story_id": str(context.story_context.story_id),
                    "chapter_id": str(context.story_context.current_chapter_id),
                    "agent_type": "narrative_intelligence",
                    "word_count": final_content["word_count"],
                    "characters": list(final_content.get("character_developments", {}).keys()),
                    "generation_timestamp": context.task_id
                },
                collection_name="context_embeddings"
            )
            
        except Exception as e:
            logger.warning(f"Failed to store generation context: {e}")
