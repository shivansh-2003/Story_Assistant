# agents/continuation_context.py
from typing import Dict, Any, List, Optional
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
import json
import logging
from datetime import datetime

from .base_agent import BaseAgent
from models.generation_models import (
    AgentContext, AgentType, ContinuationContextData,
    CharacterState, RelationshipChange, PlotThread
)
from services.vector_service import VectorService

logger = logging.getLogger(__name__)

class ContinuationContextAgent(BaseAgent):
    """
    Continuation Context Agent
    
    Responsibilities:
    - Story state persistence between chapters
    - Character emotional/mental state tracking
    - Unresolved plot thread management
    - Relationship dynamic evolution tracking
    - World state changes documentation
    - Foreshadowing and callback opportunity identification
    - Narrative tension level monitoring
    - Context compression for long stories
    - Seamless chapter transitions
    """
    
    def __init__(self, vector_service: VectorService):
        super().__init__(
            agent_type=AgentType.CONTINUATION_CONTEXT,
            vector_service=vector_service
        )
        self.context_memory: Dict[str, Dict[str, Any]] = {}
        self.compression_strategies: List[str] = [
            "key_events_extraction",
            "character_state_summary",
            "plot_thread_consolidation",
            "relationship_tracking"
        ]
    
    def _get_agent_role_description(self) -> str:
        return """
        As the Continuation Context Agent, you manage the continuity and coherence 
        of story elements across chapters and story segments, ensuring seamless 
        narrative flow and character development.
        
        Your key responsibilities:
        1. Track character emotional and mental states across story progression
        2. Monitor and manage active, dormant, and resolved plot threads
        3. Document relationship changes and dynamics between characters
        4. Maintain world state consistency across chapters
        5. Identify opportunities for foreshadowing and callbacks
        6. Compress and store essential story context for long narratives
        7. Create smooth transitions between chapters and story segments
        8. Monitor narrative tension and pacing across the entire story
        """
    
    async def _execute_task(self, context: AgentContext) -> Dict[str, Any]:
        """
        Execute Continuation Context specific tasks
        """
        task_data = context.agent_specific_data
        task_type = task_data.get("task_type", "create_continuation_context")
        
        if task_type == "create_continuation_context":
            return await self._create_continuation_context(context)
        elif task_type == "update_character_states":
            return await self._update_character_states(context)
        elif task_type == "track_plot_threads":
            return await self._track_plot_threads(context)
        elif task_type == "analyze_relationship_changes":
            return await self._analyze_relationship_changes(context)
        elif task_type == "compress_story_context":
            return await self._compress_story_context(context)
        elif task_type == "create_chapter_bridge":
            return await self._create_chapter_bridge(context)
        elif task_type == "identify_callbacks":
            return await self._identify_callback_opportunities(context)
        else:
            raise ValueError(f"Unknown task type: {task_type}")
    
    async def _create_continuation_context(self, context: AgentContext) -> Dict[str, Any]:
        """
        Create comprehensive continuation context for story progression
        """
        logger.info(f"Creating continuation context for task {context.task_id}")
        
        # 1. Analyze current content for story state
        story_state_analysis = await self._analyze_current_story_state(context)
        
        # 2. Track character states and changes
        character_tracking = await self._track_character_states(context, story_state_analysis)
        
        # 3. Identify and update plot threads
        plot_thread_analysis = await self._analyze_plot_threads(context, story_state_analysis)
        
        # 4. Track relationship dynamics
        relationship_analysis = await self._track_relationship_dynamics(context, story_state_analysis)
        
        # 5. Document world state changes
        world_state_changes = await self._document_world_state_changes(context, story_state_analysis)
        
        # 6. Identify continuation opportunities
        continuation_opportunities = await self._identify_continuation_opportunities(
            context, story_state_analysis, character_tracking, plot_thread_analysis
        )
        
        # 7. Create structured continuation context
        continuation_context = await self._structure_continuation_context(
            context, character_tracking, plot_thread_analysis, 
            relationship_analysis, world_state_changes, continuation_opportunities
        )
        
        # 8. Store context for future retrieval
        await self._store_continuation_context(context, continuation_context)
        
        return {
            "continuation_context": continuation_context,
            "character_states": character_tracking,
            "plot_threads": plot_thread_analysis,
            "relationship_changes": relationship_analysis,
            "world_state_changes": world_state_changes,
            "continuation_opportunities": continuation_opportunities,
            "context_summary": await self._create_context_summary(continuation_context)
        }
    
    async def _analyze_current_story_state(self, context: AgentContext) -> Dict[str, Any]:
        """
        Analyze the current story content to understand the story state
        """
        content = context.agent_specific_data.get("content", "")
        previous_context = context.story_context.continuation_context
        
        analysis_prompt = """
        Analyze the current story content to understand the story state:
        
        Current Content: {content}
        Previous Context: {previous_context}
        
        Story Information:
        - Genre: {genre}
        - Characters: {characters}
        
        Analyze the story state in JSON format:
        {{
            "current_scene_summary": "brief summary of what's happening now",
            "emotional_tone": "overall emotional atmosphere",
            "narrative_momentum": "high|medium|low",
            "tension_level": "high|medium|low",
            "character_activities": [
                {{
                    "character": "character name",
                    "current_activity": "what they're doing",
                    "emotional_state": "their current emotional state",
                    "goals_progress": "progress toward their goals"
                }}
            ],
            "plot_developments": ["new plot developments in this content"],
            "conflicts_introduced": ["new conflicts or tensions"],
            "conflicts_resolved": ["conflicts that were resolved"],
            "world_elements_mentioned": ["new or significant world elements"],
            "foreshadowing_elements": ["elements that might foreshadow future events"],
            "unresolved_elements": ["things left unresolved or hanging"],
            "chapter_ending_potential": "does this content end a chapter naturally?"
        }}
        """
        
        context_vars = {
            "content": content[:2000],
            "previous_context": json.dumps(previous_context) if previous_context else "No previous context",
            "genre": context.story_context.story_metadata.get("genre", "general"),
            "characters": json.dumps([char.get("name", "") for char in context.story_context.characters[:5]])
        }
        
        result = await self._generate_with_llm(
            analysis_prompt,
            context_vars,
            JsonOutputParser()
        )
        
        return result
    
    async def _track_character_states(
        self, 
        context: AgentContext, 
        story_state: Dict[str, Any]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Track character emotional and mental states
        """
        character_activities = story_state.get("character_activities", [])
        character_states = {}
        
        for activity in character_activities:
            char_name = activity.get("character", "")
            if char_name:
                char_state = await self._analyze_individual_character_state(
                    context, char_name, activity, story_state
                )
                character_states[char_name] = char_state
        
        return character_states
    
    async def _analyze_individual_character_state(
        self,
        context: AgentContext,
        character_name: str,
        current_activity: Dict[str, Any],
        story_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze individual character's current state and development
        """
        # Get character's historical context
        char_history = await self._get_character_history(character_name, context)
        
        char_analysis_prompt = """
        Analyze the current state and development of this character:
        
        Character: {character_name}
        Current Activity: {current_activity}
        Story State: {story_state}
        Character History: {char_history}
        
        Analyze character state in JSON format:
        {{
            "emotional_state": "current primary emotion",
            "mental_state": "mental/psychological condition",
            "physical_condition": "physical state if relevant",
            "current_location": "where they are",
            "immediate_goals": ["what they want to accomplish soon"],
            "long_term_goals": ["their overarching objectives"],
            "internal_conflicts": ["internal struggles they're facing"],
            "external_pressures": ["external forces affecting them"],
            "character_growth": "how they've changed recently",
            "relationship_focus": ["relationships most important to them now"],
            "unresolved_tensions": ["tensions involving this character"],
            "future_potential": ["potential directions for this character"],
            "state_changes": ["how their state has changed from before"]
        }}
        """
        
        context_vars = {
            "character_name": character_name,
            "current_activity": json.dumps(current_activity),
            "story_state": json.dumps(story_state),
            "char_history": json.dumps(char_history) if char_history else "No previous history"
        }
        
        result = await self._generate_with_llm(
            char_analysis_prompt,
            context_vars,
            JsonOutputParser()
        )
        
        return result
    
    async def _analyze_plot_threads(
        self, 
        context: AgentContext, 
        story_state: Dict[str, Any]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Analyze and track plot threads across the story
        """
        plot_developments = story_state.get("plot_developments", [])
        unresolved_elements = story_state.get("unresolved_elements", [])
        
        # Get existing plot threads from context
        existing_threads = await self._get_existing_plot_threads(context)
        
        plot_analysis_prompt = """
        Analyze plot threads based on current developments and existing threads:
        
        Current Plot Developments: {plot_developments}
        Unresolved Elements: {unresolved_elements}
        Existing Plot Threads: {existing_threads}
        
        Story Context:
        - Genre: {genre}
        - Current Scene: {current_scene}
        
        Analyze plot threads in JSON format:
        {{
            "active_threads": [
                {{
                    "thread_id": "unique identifier for the thread",
                    "description": "what this plot thread is about",
                    "status": "introduced|developing|climaxing|resolving",
                    "importance": 1-10,
                    "characters_involved": ["characters connected to this thread"],
                    "recent_developments": ["recent progress on this thread"],
                    "next_expected_development": "what might happen next"
                }}
            ],
            "resolved_threads": [
                {{
                    "thread_id": "identifier",
                    "resolution_summary": "how it was resolved",
                    "impact": "effect on story and characters"
                }}
            ],
            "dormant_threads": [
                {{
                    "thread_id": "identifier", 
                    "reason_dormant": "why this thread is currently inactive",
                    "revival_potential": "likelihood and method of revival"
                }}
            ],
            "new_threads_introduced": ["new plot threads that emerged"],
            "thread_connections": ["how different threads connect or influence each other"],
            "pacing_assessment": "how well-paced the plot development is"
        }}
        """
        
        context_vars = {
            "plot_developments": json.dumps(plot_developments),
            "unresolved_elements": json.dumps(unresolved_elements),
            "existing_threads": json.dumps(existing_threads),
            "genre": context.story_context.story_metadata.get("genre", "general"),
            "current_scene": story_state.get("current_scene_summary", "")
        }
        
        result = await self._generate_with_llm(
            plot_analysis_prompt,
            context_vars,
            JsonOutputParser()
        )
        
        return result
    
    async def _track_relationship_dynamics(
        self, 
        context: AgentContext, 
        story_state: Dict[str, Any]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Track changes in character relationships
        """
        character_activities = story_state.get("character_activities", [])
        
        if len(character_activities) < 2:
            return {}
        
        relationship_prompt = """
        Analyze relationship dynamics between characters based on their interactions:
        
        Character Activities: {character_activities}
        Story State: {story_state}
        
        Existing Characters: {characters}
        
        Analyze relationships in JSON format:
        {{
            "relationship_changes": [
                {{
                    "characters": ["character A", "character B"],
                    "relationship_type": "friendship|romance|family|rivalry|professional|etc",
                    "change_direction": "improving|deteriorating|complicated|stable",
                    "change_description": "how the relationship has changed",
                    "recent_interactions": ["recent interactions between these characters"],
                    "tension_points": ["sources of tension or conflict"],
                    "bonding_moments": ["moments that brought them closer"],
                    "future_potential": "where this relationship might go"
                }}
            ],
            "new_relationships": ["any new relationships that formed"],
            "relationship_tensions": ["overall relationship tensions in the story"],
            "relationship_opportunities": ["opportunities for relationship development"]
        }}
        """
        
        context_vars = {
            "character_activities": json.dumps(character_activities),
            "story_state": json.dumps(story_state),
            "characters": json.dumps([char.get("name", "") for char in context.story_context.characters])
        }
        
        result = await self._generate_with_llm(
            relationship_prompt,
            context_vars,
            JsonOutputParser()
        )
        
        return result
    
    async def _document_world_state_changes(
        self, 
        context: AgentContext, 
        story_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Document changes to the world state
        """
        world_elements = story_state.get("world_elements_mentioned", [])
        
        if not world_elements:
            return {"changes": [], "new_elements": [], "implications": []}
        
        world_state_prompt = """
        Document world state changes based on story developments:
        
        World Elements Mentioned: {world_elements}
        Story State: {story_context}
        Genre: {genre}
        
        Document world changes in JSON format:
        {{
            "world_state_changes": [
                {{
                    "element": "what world element changed",
                    "change_type": "new|modified|destroyed|discovered",
                    "description": "description of the change",
                    "impact": "how this affects the story world",
                    "character_impact": "how this affects characters"
                }}
            ],
            "new_world_elements": ["completely new world elements introduced"],
            "world_consistency_notes": ["notes about world consistency"],
            "implications": ["implications of these changes for future story"],
            "world_development_opportunities": ["opportunities to develop the world further"]
        }}
        """
        
        context_vars = {
            "world_elements": json.dumps(world_elements),
            "story_context": json.dumps(story_state),
            "genre": context.story_context.story_metadata.get("genre", "general")
        }
        
        result = await self._generate_with_llm(
            world_state_prompt,
            context_vars,
            JsonOutputParser()
        )
        
        return result
    
    async def _identify_continuation_opportunities(
        self,
        context: AgentContext,
        story_state: Dict[str, Any],
        character_tracking: Dict[str, Dict[str, Any]],
        plot_thread_analysis: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Identify opportunities for story continuation
        """
        continuation_prompt = """
        Identify opportunities for story continuation based on current state:
        
        Story State: {story_state}
        Character States: {character_states}
        Plot Threads: {plot_threads}
        
        Identify opportunities in JSON format:
        {{
            "immediate_continuation_hooks": [
                {{
                    "hook_type": "character|plot|world|relationship|mystery",
                    "description": "what the hook is",
                    "potential": "high|medium|low",
                    "development_direction": "how this could be developed"
                }}
            ],
            "chapter_transition_opportunities": ["natural places to transition to next chapter"],
            "tension_building_opportunities": ["ways to increase narrative tension"],
            "character_development_opportunities": ["ways to develop characters further"],
            "plot_advancement_suggestions": ["ways to advance the plot"],
            "pacing_recommendations": ["recommendations for story pacing"],
            "foreshadowing_opportunities": ["opportunities to plant foreshadowing"],
            "callback_opportunities": ["opportunities to reference earlier events"]
        }}
        """
        
        context_vars = {
            "story_state": json.dumps(story_state),
            "character_states": json.dumps(character_tracking),
            "plot_threads": json.dumps(plot_thread_analysis)
        }
        
        result = await self._generate_with_llm(
            continuation_prompt,
            context_vars,
            JsonOutputParser()
        )
        
        return result
    
    async def _structure_continuation_context(
        self,
        context: AgentContext,
        character_tracking: Dict[str, Dict[str, Any]],
        plot_thread_analysis: Dict[str, Dict[str, Any]],
        relationship_analysis: Dict[str, Dict[str, Any]],
        world_state_changes: Dict[str, Any],
        continuation_opportunities: Dict[str, Any]
    ) -> ContinuationContextData:
        """
        Structure all context into a comprehensive continuation context
        """
        # Create character states
        character_states = {}
        for char_name, char_data in character_tracking.items():
            character_states[char_name] = CharacterState(
                character_id=char_name,  # Using name as ID for simplicity
                emotional_state=char_data.get("emotional_state", "neutral"),
                physical_location=char_data.get("current_location", "unknown"),
                current_goal=", ".join(char_data.get("immediate_goals", [])),
                unresolved_tensions=char_data.get("unresolved_tensions", []),
                recent_interactions=char_data.get("relationship_focus", [])
            )
        
        # Create relationship changes
        relationship_changes = {}
        for rel_change in relationship_analysis.get("relationship_changes", []):
            rel_id = "_".join(rel_change.get("characters", []))
            relationship_changes[rel_id] = RelationshipChange(
                relationship_id=rel_id,
                status_change=rel_change.get("change_direction", "stable"),
                recent_interaction=rel_change.get("change_description", ""),
                unresolved_issues=rel_change.get("tension_points", [])
            )
        
        # Create plot threads
        plot_threads = {}
        for thread in plot_thread_analysis.get("active_threads", []):
            thread_id = thread.get("thread_id", "")
            plot_threads[thread_id] = PlotThread(
                thread_id=thread_id,
                description=thread.get("description", ""),
                status=thread.get("status", "developing"),
                importance=thread.get("importance", 5),
                related_characters=thread.get("characters_involved", [])
            )
        
        # Create continuation context
        continuation_context = ContinuationContextData(
            chapter_ending_summary=context.agent_specific_data.get("content", "")[-200:],
            character_states=character_states,
            relationship_changes=relationship_changes,
            plot_threads=plot_threads,
            world_state_changes=world_state_changes,
            emotional_momentum=plot_thread_analysis.get("pacing_assessment", "moderate"),
            suggested_next_scenes=continuation_opportunities.get("immediate_continuation_hooks", [])
        )
        
        return continuation_context
    
    async def _create_context_summary(self, continuation_context: ContinuationContextData) -> str:
        """
        Create a human-readable summary of the continuation context
        """
        summary_prompt = """
        Create a concise summary of the story continuation context:
        
        Continuation Context: {continuation_context}
        
        Create a summary that covers:
        1. Current state of main characters
        2. Active plot threads and their status
        3. Key relationship dynamics
        4. Unresolved tensions or conflicts
        5. Opportunities for story continuation
        
        Write a clear, concise summary (150-200 words) that captures the essence of where the story stands.
        """
        
        context_vars = {
            "continuation_context": json.dumps(continuation_context.dict(), indent=2)
        }
        
        result = await self._generate_with_llm(
            summary_prompt,
            context_vars,
            StrOutputParser()
        )
        
        return result
    
    async def _get_character_history(
        self, 
        character_name: str, 
        context: AgentContext
    ) -> Optional[Dict[str, Any]]:
        """
        Get character's historical context from vector database
        """
        try:
            char_history = await self._get_relevant_context(
                context.story_context,
                f"character {character_name} development history emotional state",
                "character",
                max_results=5
            )
            
            if char_history:
                return {
                    "previous_states": char_history,
                    "development_arc": "extracted from history"
                }
            
            return None
            
        except Exception as e:
            logger.warning(f"Failed to get character history for {character_name}: {e}")
            return None
    
    async def _get_existing_plot_threads(self, context: AgentContext) -> List[Dict[str, Any]]:
        """
        Get existing plot threads from vector database
        """
        try:
            plot_context = await self._get_relevant_context(
                context.story_context,
                "plot threads story arc development",
                "plot",
                max_results=10
            )
            
            return plot_context
            
        except Exception as e:
            logger.warning(f"Failed to get existing plot threads: {e}")
            return []
    
    async def _store_continuation_context(
        self,
        context: AgentContext,
        continuation_context: ContinuationContextData
    ):
        """
        Store continuation context in vector database for future retrieval
        """
        try:
            context_data = continuation_context.dict()
            
            await self._store_result_in_vector_db(
                content=json.dumps(context_data),
                metadata={
                    "story_id": str(context.story_context.story_id),
                    "chapter_id": str(context.story_context.current_chapter_id),
                    "agent_type": "continuation_context",
                    "context_type": "chapter_continuation",
                    "timestamp": context.task_id,
                    "character_count": len(context_data.get("character_states", {})),
                    "plot_thread_count": len(context_data.get("plot_threads", {}))
                },
                collection_name="context_embeddings"
            )
            
            # Update local context memory
            story_id = str(context.story_context.story_id)
            if story_id not in self.context_memory:
                self.context_memory[story_id] = {}
            
            self.context_memory[story_id]["latest_context"] = context_data
            self.context_memory[story_id]["last_updated"] = datetime.utcnow().isoformat()
            
        except Exception as e:
            logger.warning(f"Failed to store continuation context: {e}")
    
    async def _compress_story_context(self, context: AgentContext) -> Dict[str, Any]:
        """
        Compress story context for long narratives to manage memory efficiently
        """
        story_id = str(context.story_context.story_id)
        
        # Get all context for this story
        all_context = await self._get_relevant_context(
            context.story_context,
            "story context continuation character plot",
            "general",
            max_results=50
        )
        
        if not all_context:
            return {"compressed_context": {}, "compression_ratio": 0}
        
        compression_prompt = """
        Compress this story context while preserving essential information:
        
        Full Context: {full_context}
        
        Compress to essential elements in JSON format:
        {{
            "key_character_developments": ["most important character changes"],
            "critical_plot_points": ["essential plot developments"],
            "important_relationships": ["key relationship changes"],
            "world_state_essentials": ["crucial world state information"],
            "unresolved_tensions": ["important unresolved elements"],
            "foreshadowing_elements": ["important foreshadowing to remember"],
            "context_timeline": ["chronological order of key events"],
            "compression_notes": ["what was compressed and why"]
        }}
        """
        
        context_vars = {
            "full_context": json.dumps(all_context[:20])  # Limit for prompt size
        }
        
        compressed = await self._generate_with_llm(
            compression_prompt,
            context_vars,
            JsonOutputParser()
        )
        
        # Calculate compression ratio
        original_size = len(json.dumps(all_context))
        compressed_size = len(json.dumps(compressed))
        compression_ratio = compressed_size / original_size if original_size > 0 else 0
        
        return {
            "compressed_context": compressed,
            "compression_ratio": compression_ratio,
            "original_elements": len(all_context),
            "compressed_elements": len(compressed.get("key_character_developments", [])) + 
                                 len(compressed.get("critical_plot_points", []))
        }
    
    async def _identify_callback_opportunities(self, context: AgentContext) -> Dict[str, Any]:
        """
        Identify opportunities for callbacks to earlier story elements
        """
        current_content = context.agent_specific_data.get("content", "")
        
        # Get historical story context
        historical_context = await self._get_relevant_context(
            context.story_context,
            "early story events character introduction plot setup",
            "general",
            max_results=10
        )
        
        callback_prompt = """
        Identify callback opportunities to earlier story elements:
        
        Current Content: {current_content}
        Historical Context: {historical_context}
        
        Identify callbacks in JSON format:
        {{
            "direct_callback_opportunities": [
                {{
                    "historical_element": "what from the past could be referenced",
                    "current_connection": "how it connects to current events",
                    "callback_type": "character|plot|world|theme|dialogue",
                    "impact_potential": "high|medium|low",
                    "implementation_suggestion": "how to implement the callback"
                }}
            ],
            "thematic_callback_opportunities": ["thematic elements that could echo earlier themes"],
            "character_arc_callbacks": ["ways to reference character development"],
            "foreshadowing_payoffs": ["earlier foreshadowing that could be paid off"],
            "easter_egg_opportunities": ["subtle references for attentive readers"]
        }}
        """
        
        context_vars = {
            "current_content": current_content[:1000],
            "historical_context": json.dumps(historical_context[:5])
        }
        
        result = await self._generate_with_llm(
            callback_prompt,
            context_vars,
            JsonOutputParser()
        )
        
        return result
