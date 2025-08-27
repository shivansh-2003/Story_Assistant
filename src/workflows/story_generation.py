# workflows/story_generation_workflow.py
from typing import Dict, Any, List, Optional, TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor
from langchain_core.messages import HumanMessage, AIMessage
import asyncio
import logging
import json
from datetime import datetime

from agents.creative_director_agent import CreativeDirectorAgent
from agents.narrative_intelligence_agent import NarrativeIntelligenceAgent
from agents.quality_assurance_agent import QualityAssuranceAgent
from agents.world_building_agent import WorldBuildingAgent
from agents.visual_storytelling_agent import VisualStorytellingAgent
from agents.continuation_context_agent import ContinuationContextAgent
from services.vector_service import get_vector_service
from models.generation_models import (
    AgentContext, StoryContext, GenerationType,
    AgentType, TaskStatus, ContentGenerationContext
)

logger = logging.getLogger(__name__)

class StoryGenerationState(TypedDict):
    """State management for story generation workflow"""
    task_id: str
    story_context: Dict[str, Any]
    user_input: str
    generation_mode: str
    target_word_count: int
    include_images: bool
    
    # Agent results
    orchestration_result: Optional[Dict[str, Any]]
    narrative_result: Optional[Dict[str, Any]]
    quality_result: Optional[Dict[str, Any]]
    world_result: Optional[Dict[str, Any]]
    visual_result: Optional[Dict[str, Any]]
    context_result: Optional[Dict[str, Any]]
    
    # Workflow state
    current_step: str
    completed_steps: List[str]
    failed_steps: List[str]
    retry_count: int
    final_result: Optional[Dict[str, Any]]
    
    # Error handling
    errors: List[str]
    should_retry: bool
    

class StoryGenerationWorkflow:
    """
    LangGraph-based workflow for orchestrating story generation across multiple agents
    """
    
    def __init__(self):
        self.agents: Dict[str, Any] = {}
        self.workflow = None
        self.vector_service = None
        self.initialized = False
    
    async def initialize(self):
        """Initialize workflow with agents and graph"""
        try:
            # Get vector service
            self.vector_service = await get_vector_service()
            
            # Initialize agents
            self.agents = {
                'creative_director': CreativeDirectorAgent(self.vector_service),
                'narrative_intelligence': NarrativeIntelligenceAgent(self.vector_service),
                'quality_assurance': QualityAssuranceAgent(self.vector_service),
                'world_building': WorldBuildingAgent(self.vector_service),
                'visual_storytelling': VisualStorytellingAgent(self.vector_service),
                'continuation_context': ContinuationContextAgent(self.vector_service)
            }
            
            # Build workflow graph
            self.workflow = self._build_workflow_graph()
            
            self.initialized = True
            logger.info("Story generation workflow initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize story generation workflow: {e}")
            raise
    
    def _build_workflow_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(StoryGenerationState)
        
        # Add nodes for each step
        workflow.add_node("orchestrate", self._orchestrate_step)
        workflow.add_node("analyze_context", self._analyze_context_step)
        workflow.add_node("generate_narrative", self._generate_narrative_step)
        workflow.add_node("enhance_world", self._enhance_world_step)
        workflow.add_node("check_quality", self._check_quality_step)
        workflow.add_node("generate_visuals", self._generate_visuals_step)
        workflow.add_node("finalize_output", self._finalize_output_step)
        workflow.add_node("handle_error", self._handle_error_step)
        
        # Define workflow edges
        workflow.set_entry_point("orchestrate")
        
        # Main workflow path
        workflow.add_edge("orchestrate", "analyze_context")
        workflow.add_conditional_edges(
            "analyze_context",
            self._should_enhance_world,
            {
                "enhance_world": "enhance_world",
                "generate_narrative": "generate_narrative"
            }
        )
        workflow.add_edge("enhance_world", "generate_narrative")
        workflow.add_edge("generate_narrative", "check_quality")
        
        # Quality check branching
        workflow.add_conditional_edges(
            "check_quality",
            self._quality_check_routing,
            {
                "retry_narrative": "generate_narrative",
                "generate_visuals": "generate_visuals",
                "finalize": "finalize_output",
                "error": "handle_error"
            }
        )
        
        # Visual generation branching
        workflow.add_conditional_edges(
            "generate_visuals",
            self._should_generate_visuals,
            {
                "finalize": "finalize_output",
                "skip_visuals": "finalize_output"
            }
        )
        
        # Error handling
        workflow.add_conditional_edges(
            "handle_error",
            self._error_recovery_routing,
            {
                "retry": "orchestrate",
                "error": "finalize_output",
                "end": END
            }
        )
        
        workflow.add_edge("finalize_output", END)
        
        return workflow.compile()
    
    async def execute_workflow(
        self,
        task_id: str,
        story_context: StoryContext,
        user_input: str,
        generation_mode: str = "ai_guided",
        target_word_count: int = 250,
        include_images: bool = False
    ) -> Dict[str, Any]:
        """
        Execute the complete story generation workflow
        
        Args:
            task_id: Unique task identifier
            story_context: Story context information
            user_input: User's input/direction
            generation_mode: Mode of generation
            target_word_count: Target word count for generation
            include_images: Whether to generate images
            
        Returns:
            Final generation result
        """
        if not self.initialized:
            await self.initialize()
        
        # Initialize state
        initial_state = StoryGenerationState(
            task_id=task_id,
            story_context=story_context.dict(),
            user_input=user_input,
            generation_mode=generation_mode,
            target_word_count=target_word_count,
            include_images=include_images,
            
            orchestration_result=None,
            narrative_result=None,
            quality_result=None,
            world_result=None,
            visual_result=None,
            context_result=None,
            
            current_step="orchestrate",
            completed_steps=[],
            failed_steps=[],
            retry_count=0,
            final_result=None,
            
            errors=[],
            should_retry=False,
    
        )
        
        try:
            # Execute workflow
            logger.info(f"Starting story generation workflow for task {task_id}")
            
            final_state = await self.workflow.ainvoke(initial_state)
            
            logger.info(f"Workflow completed for task {task_id}")
            return final_state.get("final_result", {})
            
        except Exception as e:
            logger.error(f"Workflow execution failed for task {task_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "task_id": task_id,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    # Workflow step implementations
    
    async def _orchestrate_step(self, state: StoryGenerationState) -> StoryGenerationState:
        """Creative Director orchestration step"""
        try:
            logger.info(f"Executing orchestrate step for task {state['task_id']}")
            
            # Create agent context
            agent_context = AgentContext(
                agent_type=AgentType.CREATIVE_DIRECTOR,
                task_id=state["task_id"],
                story_context=StoryContext(**state["story_context"]),
                user_input=state["user_input"],
                agent_specific_data={
                    "task_type": "orchestrate_generation",
                    "generation_mode": state["generation_mode"],
                    "target_word_count": state["target_word_count"],
                    "include_images": state["include_images"]
                }
            )
            
            # Execute Creative Director
            response = await self.agents['creative_director'].process_request(agent_context)
            
            if response.success:
                state["orchestration_result"] = response.result
                state["completed_steps"].append("orchestrate")
                state["current_step"] = "analyze_context"
            else:
                state["errors"].append(f"Orchestration failed: {response.error}")
                state["failed_steps"].append("orchestrate")
                state["should_retry"] = True
            
            return state
            
        except Exception as e:
            logger.error(f"Orchestrate step failed: {e}")
            state["errors"].append(f"Orchestrate step error: {str(e)}")
            state["failed_steps"].append("orchestrate")
            return state
    
    async def _analyze_context_step(self, state: StoryGenerationState) -> StoryGenerationState:
        """Continuation Context analysis step"""
        try:
            logger.info(f"Executing analyze_context step for task {state['task_id']}")
            
            agent_context = AgentContext(
                agent_type=AgentType.CONTINUATION_CONTEXT,
                task_id=state["task_id"],
                story_context=StoryContext(**state["story_context"]),
                user_input=state["user_input"],
                agent_specific_data={
                    "task_type": "create_continuation_context",
                    "content": ""  # Will be populated with any existing content
                }
            )
            
            response = await self.agents['continuation_context'].process_request(agent_context)
            
            if response.success:
                state["context_result"] = response.result
                state["completed_steps"].append("analyze_context")
                state["current_step"] = "generate_narrative"
            else:
                state["errors"].append(f"Context analysis failed: {response.error}")
                state["failed_steps"].append("analyze_context")
            
            return state
            
        except Exception as e:
            logger.error(f"Analyze context step failed: {e}")
            state["errors"].append(f"Context analysis error: {str(e)}")
            state["failed_steps"].append("analyze_context")
            return state
    
    async def _generate_narrative_step(self, state: StoryGenerationState) -> StoryGenerationState:
        """Narrative Intelligence generation step"""
        try:
            logger.info(f"Executing generate_narrative step for task {state['task_id']}")
            
            # Prepare narrative context from previous steps
            narrative_context = {}
            if state.get("orchestration_result"):
                narrative_context.update(state["orchestration_result"])
            if state.get("context_result"):
                narrative_context.update(state["context_result"])
            
            agent_context = AgentContext(
                agent_type=AgentType.NARRATIVE_INTELLIGENCE,
                task_id=state["task_id"],
                story_context=StoryContext(**state["story_context"]),
                user_input=state["user_input"],
                agent_specific_data={
                    "task_type": "generate_content",
                    "target_word_count": state["target_word_count"],
                    "generation_mode": state["generation_mode"],
                    "narrative_context": narrative_context
                }
            )
            
            response = await self.agents['narrative_intelligence'].process_request(agent_context)
            
            if response.success:
                state["narrative_result"] = response.result
                state["completed_steps"].append("generate_narrative")
                state["current_step"] = "check_quality"
            else:
                state["errors"].append(f"Narrative generation failed: {response.error}")
                state["failed_steps"].append("generate_narrative")
                state["should_retry"] = True
            
            return state
            
        except Exception as e:
            logger.error(f"Generate narrative step failed: {e}")
            state["errors"].append(f"Narrative generation error: {str(e)}")
            state["failed_steps"].append("generate_narrative")
            return state
    
    async def _enhance_world_step(self, state: StoryGenerationState) -> StoryGenerationState:
        """World Building enhancement step"""
        try:
            logger.info(f"Executing enhance_world step for task {state['task_id']}")
            
            # Get content from narrative result if available
            content = ""
            if state.get("narrative_result"):
                content = state["narrative_result"].get("content", "")
            
            agent_context = AgentContext(
                agent_type=AgentType.WORLD_BUILDING,
                task_id=state["task_id"],
                story_context=StoryContext(**state["story_context"]),
                user_input=state["user_input"],
                agent_specific_data={
                    "task_type": "enhance_setting",
                    "content": content
                }
            )
            
            response = await self.agents['world_building'].process_request(agent_context)
            
            if response.success:
                state["world_result"] = response.result
                state["completed_steps"].append("enhance_world")
            else:
                # World building failure is not critical
                logger.warning(f"World building failed: {response.error}")
                state["world_result"] = {"setting_enhancements": {}}
            
            return state
            
        except Exception as e:
            logger.warning(f"Enhance world step failed: {e}")
            state["world_result"] = {"setting_enhancements": {}}
            return state
    
    async def _check_quality_step(self, state: StoryGenerationState) -> StoryGenerationState:
        """Quality Assurance check step"""
        try:
            logger.info(f"Executing check_quality step for task {state['task_id']}")
            
            # Get content to check
            content = ""
            if state.get("narrative_result"):
                content = state["narrative_result"].get("content", "")
            
            if not content:
                state["errors"].append("No content available for quality check")
                return state
            
            agent_context = AgentContext(
                agent_type=AgentType.QUALITY_ASSURANCE,
                task_id=state["task_id"],
                story_context=StoryContext(**state["story_context"]),
                user_input=state["user_input"],
                agent_specific_data={
                    "task_type": "full_quality_check",
                    "content": content
                }
            )
            
            response = await self.agents['quality_assurance'].process_request(agent_context)
            
            if response.success:
                state["quality_result"] = response.result
                state["completed_steps"].append("check_quality")
                state["current_step"] = "generate_visuals" if state["include_images"] else "finalize_output"
            else:
                state["errors"].append(f"Quality check failed: {response.error}")
                state["failed_steps"].append("check_quality")
            
            return state
            
        except Exception as e:
            logger.error(f"Quality check step failed: {e}")
            state["errors"].append(f"Quality check error: {str(e)}")
            state["failed_steps"].append("check_quality")
            return state
    
    async def _generate_visuals_step(self, state: StoryGenerationState) -> StoryGenerationState:
        """Visual Storytelling generation step"""
        try:
            logger.info(f"Executing generate_visuals step for task {state['task_id']}")
            
            # Get content for visual generation
            content = ""
            if state.get("narrative_result"):
                content = state["narrative_result"].get("content", "")
            
            agent_context = AgentContext(
                agent_type=AgentType.VISUAL_STORYTELLING,
                task_id=state["task_id"],
                story_context=StoryContext(**state["story_context"]),
                user_input=state["user_input"],
                agent_specific_data={
                    "task_type": "analyze_scene",
                    "content": content
                }
            )
            
            response = await self.agents['visual_storytelling'].process_request(agent_context)
            
            if response.success:
                state["visual_result"] = response.result
                state["completed_steps"].append("generate_visuals")
            else:
                # Visual generation failure is not critical
                logger.warning(f"Visual generation failed: {response.error}")
                state["visual_result"] = {"image_generation_prompt": ""}
            
            state["current_step"] = "finalize_output"
            return state
            
        except Exception as e:
            logger.warning(f"Generate visuals step failed: {e}")
            state["visual_result"] = {"image_generation_prompt": ""}
            return state
    
    async def _finalize_output_step(self, state: StoryGenerationState) -> StoryGenerationState:
        """Finalize and assemble output step"""
        try:
            logger.info(f"Executing finalize_output step for task {state['task_id']}")
            
            # Assemble final result from all agent outputs
            final_result = {
                "success": True,
                "task_id": state["task_id"],
                "timestamp": datetime.utcnow().isoformat(),
                "content": "",
                "word_count": 0,
                "quality_metrics": {},
                "world_enhancements": {},
                "visual_elements": {},
                "continuation_context": {},
                "generation_metadata": {
                    "completed_steps": state["completed_steps"],
                    "failed_steps": state["failed_steps"],
                    "retry_count": state["retry_count"],
                    "generation_mode": state["generation_mode"],
                    "target_word_count": state["target_word_count"]
                }
            }
            
            # Extract content from narrative result
            if state.get("narrative_result"):
                narrative = state["narrative_result"]
                final_result["content"] = narrative.get("content", "")
                final_result["word_count"] = narrative.get("word_count", 0)
                final_result["character_consistency_scores"] = narrative.get("character_consistency_scores", {})
            
            # Extract quality metrics
            if state.get("quality_result"):
                quality = state["quality_result"]
                final_result["quality_metrics"] = quality.get("quality_metrics", {})
                final_result["improvement_suggestions"] = quality.get("improvement_suggestions", [])
                final_result["requires_human_review"] = quality.get("requires_human_review", False)
            
            # Extract world enhancements
            if state.get("world_result"):
                final_result["world_enhancements"] = state["world_result"].get("setting_enhancements", {})
            
            # Extract visual elements
            if state.get("visual_result"):
                final_result["visual_elements"] = {
                    "image_prompt": state["visual_result"].get("image_generation_prompt", ""),
                    "scene_elements": state["visual_result"].get("scene_elements", [])
                }
            
            # Extract continuation context
            if state.get("context_result"):
                final_result["continuation_context"] = state["context_result"].get("continuation_context", {})
            
            # Add error information if any
            if state["errors"]:
                final_result["warnings"] = state["errors"]
                final_result["partial_success"] = True
            
            state["final_result"] = final_result
            state["completed_steps"].append("finalize_output")
            
            logger.info(f"Workflow finalized for task {state['task_id']}")
            return state
            
        except Exception as e:
            logger.error(f"Finalize output step failed: {e}")
            state["errors"].append(f"Finalization error: {str(e)}")
            
            # Create minimal error result
            state["final_result"] = {
                "success": False,
                "task_id": state["task_id"],
                "error": "Failed to finalize output",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return state
    
    async def _handle_error_step(self, state: StoryGenerationState) -> StoryGenerationState:
        """Handle workflow errors and determine recovery strategy"""
        try:
            logger.warning(f"Handling errors for task {state['task_id']}: {state['errors']}")
            
            # Increment retry count
            state["retry_count"] += 1
            
            # Determine if we should retry or terminate
            if state["retry_count"] < 3:
                # Retry with same configuration
                state["should_retry"] = True
                state["current_step"] = "orchestrate"
                state["failed_steps"] = []  # Reset failed steps for retry
                logger.info(f"Retrying workflow for task {state['task_id']} (attempt {state['retry_count']})")
            
            else:
                # Give up and create error result
                state["final_result"] = {
                    "success": False,
                    "task_id": state["task_id"],
                    "error": "Workflow failed after multiple retries",
                    "errors": state["errors"],
                    "retry_count": state["retry_count"],
                    "timestamp": datetime.utcnow().isoformat()
                }
                logger.error(f"Workflow failed permanently for task {state['task_id']}")
            
            return state
            
        except Exception as e:
            logger.error(f"Error handling step failed: {e}")
            state["final_result"] = {
                "success": False,
                "task_id": state["task_id"],
                "error": "Critical workflow failure",
                "timestamp": datetime.utcnow().isoformat()
            }
            return state
    
    # Conditional routing functions
    
    def _should_enhance_world(self, state: StoryGenerationState) -> str:
        """Determine if world building enhancement is needed"""
        orchestration_result = state.get("orchestration_result", {})
        orchestration_plan = orchestration_result.get("orchestration_plan", {})
        workflow_plan = orchestration_plan.get("workflow_plan", {})
        
        agent_sequence = workflow_plan.get("agent_sequence", [])
        
        if "world_building" in agent_sequence:
            return "enhance_world"
        else:
            return "generate_narrative"
    
    def _quality_check_routing(self, state: StoryGenerationState) -> str:
        """Route based on quality check results"""
        quality_result = state.get("quality_result", {})
        
        if not quality_result:
            return "error"
        
        quality_metrics = quality_result.get("quality_metrics", {})
        overall_score = quality_metrics.get("overall_quality_score", 0.5)
        
        # If quality is too low and we haven't retried too much
        if overall_score < 0.6 and state["retry_count"] < 2:
            return "retry_narrative"
        
        # If we should generate visuals
        elif state["include_images"]:
            return "generate_visuals"
        
        # Otherwise finalize
        else:
            return "finalize"
    
    def _should_generate_visuals(self, state: StoryGenerationState) -> str:
        """Determine if visual generation completed successfully"""
        visual_result = state.get("visual_result", {})
        
        # Always proceed to finalize (visual failure is not critical)
        return "finalize"
    
    def _error_recovery_routing(self, state: StoryGenerationState) -> str:
        """Route error recovery based on state"""
        if state.get("should_retry", False):
            return "retry"
        elif state.get("final_result"):
            return "end"
        else:
            return "error"

# Global workflow instance
story_workflow = StoryGenerationWorkflow()

# Convenience function
async def execute_story_generation(
    task_id: str,
    story_context: StoryContext,
    user_input: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Execute story generation workflow
    
    Args:
        task_id: Unique task identifier
        story_context: Story context information
        user_input: User's input/direction
        **kwargs: Additional workflow parameters
        
    Returns:
        Generation result
    """
    if not story_workflow.initialized:
        await story_workflow.initialize()
    
    return await story_workflow.execute_workflow(
        task_id=task_id,
        story_context=story_context,
        user_input=user_input,
        **kwargs
    )
