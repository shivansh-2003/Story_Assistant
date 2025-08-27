# agents/creative_director.py
from typing import Dict, Any, List, Optional
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
import json
import logging

from .base_agent import BaseAgent
from models.generation_models import (
    AgentContext, AgentType, StoryContext,
    ContentGenerationContext, GenerationType
)
from services.vector_service import VectorService

logger = logging.getLogger(__name__)

class CreativeDirectorAgent(BaseAgent):
    """
    Creative Director Agent - Master Orchestrator
    
    Responsibilities:
    - Cross-chapter context continuity management
    - Dynamic generation flow orchestration
    - User interaction state tracking (AI-only vs guided mode)
    - Generation token/word budget management
    - Image generation toggle coordination
    - Poster creation workflow initiation
    - Task planning and delegation to other agents
    - Quality gate management
    - Final output assembly
    """
    
    def __init__(self, vector_service: VectorService):
        super().__init__(
            agent_type=AgentType.CREATIVE_DIRECTOR,
            vector_service=vector_service
        )
        self.orchestration_history: List[Dict[str, Any]] = []
    
    def _get_agent_role_description(self) -> str:
        return """
        As the Creative Director, you are the master orchestrator of the story generation process.
        You analyze user requests, plan the generation workflow, coordinate other agents,
        and ensure the final output meets quality standards while maintaining narrative coherence.
        
        Your key responsibilities:
        1. Interpret user intent and break down complex requests
        2. Plan multi-agent workflows for optimal story generation
        3. Manage context continuity across chapters and segments
        4. Coordinate with specialized agents (Narrative, Quality, World-building, etc.)
        5. Make decisions about image generation and visual elements
        6. Ensure consistency with story metadata and user preferences
        7. Assemble final outputs from multiple agent contributions
        """
    
    async def _execute_task(self, context: AgentContext) -> Dict[str, Any]:
        """
        Execute Creative Director specific tasks based on the request type
        """
        task_data = context.agent_specific_data
        task_type = task_data.get("task_type", "orchestrate_generation")
        
        if task_type == "orchestrate_generation":
            return await self._orchestrate_story_generation(context)
        elif task_type == "plan_workflow":
            return await self._plan_generation_workflow(context)
        elif task_type == "analyze_user_intent":
            return await self._analyze_user_intent(context)
        elif task_type == "assemble_final_output":
            return await self._assemble_final_output(context)
        elif task_type == "manage_continuity":
            return await self._manage_chapter_continuity(context)
        else:
            raise ValueError(f"Unknown task type: {task_type}")
    
    async def _orchestrate_story_generation(self, context: AgentContext) -> Dict[str, Any]:
        """
        Main orchestration method for story generation
        """
        logger.info(f"Orchestrating story generation for task {context.task_id}")
        
        # 1. Analyze user intent and requirements
        intent_analysis = await self._analyze_user_intent(context)
        
        # 2. Plan the generation workflow
        workflow_plan = await self._plan_generation_workflow(context, intent_analysis)
        
        # 3. Gather relevant context from vector database
        story_context = await self._gather_story_context(context)
        
        # 4. Create generation strategy
        generation_strategy = await self._create_generation_strategy(
            context, intent_analysis, workflow_plan, story_context
        )
        
        # 5. Determine resource allocation
        resource_plan = self._plan_resource_allocation(context, generation_strategy)
        
        return {
            "orchestration_plan": {
                "intent_analysis": intent_analysis,
                "workflow_plan": workflow_plan,
                "story_context": story_context,
                "generation_strategy": generation_strategy,
                "resource_plan": resource_plan
            },
            "next_agents": workflow_plan.get("agent_sequence", []),
            "estimated_completion_time": resource_plan.get("estimated_time_seconds", 60),
            "requires_images": generation_strategy.get("include_images", False),
            "continuation_context": story_context.get("continuation_context", {})
        }
    
    async def _analyze_user_intent(self, context: AgentContext) -> Dict[str, Any]:
        """
        Analyze user input to understand their intent and requirements
        """
        user_input = context.user_input or ""
        story_context = context.story_context
        
        analysis_prompt = """
        Analyze the following user input for story generation and determine their intent:
        
        User Input: "{user_input}"
        
        Story Context:
        - Current Chapter: {current_chapter}
        - Genre: {genre}
        - Writing Style: {writing_style}
        - Previous Content Length: {content_length} words
        
        Provide your analysis in the following JSON format:
        {{
            "intent_type": "continue_story|new_chapter|character_development|world_building|revision|other",
            "generation_type": "narrative|dialogue|description|action|mixed",
            "target_length": "estimated word count",
            "tone_direction": "maintain|lighter|darker|more_serious|more_humorous",
            "focus_areas": ["plot", "character", "setting", "dialogue"],
            "specific_requirements": ["list of specific user requirements"],
            "continuity_needs": ["previous context that must be maintained"],
            "creative_freedom_level": "high|medium|low",
            "urgency": "immediate|normal|background",
            "complexity_level": 1-5
        }}
        """
        
        context_vars = {
            "user_input": user_input,
            "current_chapter": story_context.current_chapter_id or "Starting new story",
            "genre": story_context.story_metadata.get("genre", "Unknown"),
            "writing_style": story_context.story_metadata.get("writing_style", "Unknown"),
            "content_length": len(story_context.previous_content or "")
        }
        
        result = await self._generate_with_llm(
            analysis_prompt,
            context_vars,
            JsonOutputParser()
        )
        
        return result
    
    async def _plan_generation_workflow(
        self, 
        context: AgentContext, 
        intent_analysis: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Plan the multi-agent workflow based on user intent and story requirements
        """
        if not intent_analysis:
            intent_analysis = await self._analyze_user_intent(context)
        
        workflow_prompt = """
        Based on the user intent analysis, plan the optimal workflow for story generation:
        
        Intent Analysis: {intent_analysis}
        
        Story Context:
        - Genre: {genre}
        - Current Chapter: {current_chapter}
        - Image Settings Enabled: {images_enabled}
        
        Available Agents:
        1. narrative_intelligence - Story content generation and character voice consistency
        2. quality_assurance - Grammar, consistency, and quality validation
        3. world_building - Setting details and world consistency
        4. visual_storytelling - Image generation and visual elements
        5. continuation_context - Context management and chapter transitions
        
        Create a workflow plan in JSON format:
        {{
            "agent_sequence": ["ordered list of agents to execute"],
            "parallel_groups": [["agents that can run in parallel"]],
            "dependencies": {{"agent": ["required_previous_agents"]}},
            "conditional_agents": {{"condition": "agent_to_include_if_true"}},
            "estimated_steps": "number of workflow steps",
            "complexity_score": 1-5,
            "risk_factors": ["potential issues to watch for"]
        }}
        """
        
        context_vars = {
            "intent_analysis": json.dumps(intent_analysis, indent=2),
            "genre": context.story_context.story_metadata.get("genre", "Unknown"),
            "current_chapter": context.story_context.current_chapter_id or "New story",
            "images_enabled": context.story_context.image_settings.get("enabled", False)
        }
        
        result = await self._generate_with_llm(
            workflow_prompt,
            context_vars,
            JsonOutputParser()
        )
        
        return result
    
    async def _gather_story_context(self, context: AgentContext) -> Dict[str, Any]:
        """
        Gather relevant story context from vector database and story metadata
        """
        story_context = context.story_context
        user_input = context.user_input or ""
        
        # Search for relevant context based on user input
        search_query = f"{user_input} {story_context.story_metadata.get('genre', '')}"
        
        # Get different types of context
        contexts = {}
        
        # Character context
        if story_context.characters:
            character_context = await self._get_relevant_context(
                story_context, search_query, "character", max_results=3
            )
            contexts["characters"] = character_context
        
        # Plot context
        plot_context = await self._get_relevant_context(
            story_context, search_query, "plot", max_results=5
        )
        contexts["plot_points"] = plot_context
        
        # World context
        world_context = await self._get_relevant_context(
            story_context, search_query, "world", max_results=3
        )
        contexts["world_elements"] = world_context
        
        # Previous content context
        if story_context.previous_content:
            contexts["previous_content_summary"] = story_context.previous_content[-1000:]  # Last 1000 chars
        
        # Continuation context
        contexts["continuation_context"] = story_context.continuation_context
        
        return contexts
    
    async def _create_generation_strategy(
        self,
        context: AgentContext,
        intent_analysis: Dict[str, Any],
        workflow_plan: Dict[str, Any],
        story_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a comprehensive generation strategy
        """
        strategy_prompt = """
        Create a detailed generation strategy based on the analysis and planning:
        
        Intent Analysis: {intent_analysis}
        Workflow Plan: {workflow_plan}
        Available Context: {context_summary}
        
        Generation Settings:
        - Words per segment: {words_per_segment}
        - Writing style: {writing_style}
        - Temperature: {temperature}
        
        Create a generation strategy in JSON format:
        {{
            "content_approach": "descriptive|dialogue_heavy|action_packed|balanced",
            "narrative_perspective": "first_person|third_person_limited|third_person_omniscient",
            "pacing_strategy": "slow_build|moderate|fast_paced|varied",
            "character_focus": ["list of characters to emphasize"],
            "plot_advancement": "major|minor|setup|resolution",
            "include_images": true/false,
            "image_triggers": ["scene_changes", "character_introductions", "action_sequences"],
            "quality_thresholds": {{"consistency": 0.8, "coherence": 0.85, "grammar": 0.9}},
            "continuity_anchors": ["key elements that must be maintained"]
        }}
        """
        
        context_vars = {
            "intent_analysis": json.dumps(intent_analysis, indent=2),
            "workflow_plan": json.dumps(workflow_plan, indent=2),
            "context_summary": str(list(story_context.keys())),
            "words_per_segment": context.story_context.generation_settings.get("words_per_segment", 250),
            "writing_style": context.story_context.story_metadata.get("writing_style", "balanced"),
            "temperature": context.story_context.generation_settings.get("temperature", 0.7)
        }
        
        result = await self._generate_with_llm(
            strategy_prompt,
            context_vars,
            JsonOutputParser()
        )
        
        return result
    
    def _plan_resource_allocation(
        self, 
        context: AgentContext, 
        generation_strategy: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Plan resource allocation for the generation task
        """
        # Estimate based on complexity and requirements
        complexity = generation_strategy.get("complexity_score", 3)
        word_target = context.agent_specific_data.get("target_word_count", 250)
        include_images = generation_strategy.get("include_images", False)
        
        # Base time estimates (in seconds)
        base_time = 30
        complexity_multiplier = complexity * 0.5
        word_multiplier = (word_target / 250) * 0.3
        image_multiplier = 20 if include_images else 0
        
        estimated_time = int(base_time + (base_time * complexity_multiplier) + 
                           (base_time * word_multiplier) + image_multiplier)
        
        return {
            "estimated_time_seconds": estimated_time,
            "complexity_score": complexity,
            "resource_requirements": {
                "llm_calls": complexity + 2,
                "vector_searches": complexity,
                "image_generations": 1 if include_images else 0
            },
            "priority_level": context.agent_specific_data.get("priority", 5),
            "max_retries": 2 if complexity < 4 else 3
        }
    
    async def _manage_chapter_continuity(self, context: AgentContext) -> Dict[str, Any]:
        """
        Manage continuity between chapters and story segments
        """
        continuity_prompt = """
        Analyze the story context and create a continuity plan for seamless transitions:
        
        Current Context: {story_context}
        Previous Content: {previous_content}
        User Direction: {user_input}
        
        Create a continuity management plan:
        {{
            "character_states": {{"character_id": "current emotional and physical state"}},
            "plot_threads": {{"thread_name": "current status and direction"}},
            "world_state": "current state of the story world",
            "unresolved_tensions": ["list of unresolved conflicts"],
            "transition_opportunities": ["natural points to transition or develop"],
            "consistency_checks": ["elements that need consistency verification"],
            "context_summary": "key information to carry forward"
        }}
        """
        
        context_vars = {
            "story_context": json.dumps(context.story_context.story_metadata, indent=2),
            "previous_content": context.story_context.previous_content or "No previous content",
            "user_input": context.user_input or "Continue story naturally"
        }
        
        result = await self._generate_with_llm(
            continuity_prompt,
            context_vars,
            JsonOutputParser()
        )
        
        return result
    
    async def _assemble_final_output(self, context: AgentContext) -> Dict[str, Any]:
        """
        Assemble final output from multiple agent contributions
        """
        agent_results = context.previous_agent_results
        
        # Extract content from different agents
        narrative_content = ""
        quality_feedback = {}
        world_additions = {}
        visual_elements = []
        
        for result in agent_results:
            agent_type = result.get("agent_type", "unknown")
            
            if agent_type == "narrative_intelligence":
                narrative_content = result.get("content", "")
            elif agent_type == "quality_assurance":
                quality_feedback = result.get("quality_metrics", {})
            elif agent_type == "world_building":
                world_additions = result.get("world_elements", {})
            elif agent_type == "visual_storytelling":
                visual_elements = result.get("generated_images", [])
        
        # Create final assembly
        assembly_prompt = """
        Assemble the final story output from agent contributions:
        
        Narrative Content: {narrative_content}
        Quality Feedback: {quality_feedback}
        World Elements: {world_additions}
        Visual Elements: {visual_elements}
        
        Create a final assembly in JSON format:
        {{
            "final_content": "polished final story content",
            "word_count": "total word count",
            "quality_score": "overall quality rating 0-1",
            "improvements_made": ["list of improvements from quality feedback"],
            "visual_integration": ["how visual elements are integrated"],
            "continuation_notes": "notes for future generation",
            "metadata": {{"generation_summary": "summary of generation process"}}
        }}
        """
        
        context_vars = {
            "narrative_content": narrative_content[:2000],  # Truncate for prompt
            "quality_feedback": json.dumps(quality_feedback),
            "world_additions": json.dumps(world_additions),
            "visual_elements": str(visual_elements)
        }
        
        result = await self._generate_with_llm(
            assembly_prompt,
            context_vars,
            JsonOutputParser()
        )
        
        return result
    
    def _get_next_agents(self, context: AgentContext, result: Dict[str, Any]) -> List[str]:
        """
        Determine next agents based on orchestration plan
        """
        orchestration_plan = result.get("orchestration_plan", {})
        workflow_plan = orchestration_plan.get("workflow_plan", {})
        
        return workflow_plan.get("agent_sequence", [])
    
    async def _validate_agent_specific_context(self, context: AgentContext) -> None:
        """
        Validate Creative Director specific context requirements
        """
        # Ensure we have necessary story context
        if not context.story_context.story_metadata:
            logger.warning("Limited story metadata available for orchestration")
        
        # Check if this is a continuation that needs previous context
        task_type = context.agent_specific_data.get("task_type", "")
        if "continue" in task_type.lower() and not context.story_context.previous_content:
            logger.warning("Continuation requested but no previous content available")
