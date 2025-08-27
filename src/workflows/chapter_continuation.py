# workflows/chapter_continuation_workflow.py
from typing import Dict, Any, List, Optional, TypedDict
from langgraph.graph import StateGraph, END
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
    AgentType, TaskStatus
)

logger = logging.getLogger(__name__)

class ChapterContinuationState(TypedDict):
    """State management for chapter continuation workflow"""
    task_id: str
    story_context: Dict[str, Any]
    chapter_id: str
    previous_content: str
    user_direction: Optional[str]
    continuation_mode: str  # seamless, user_guided, chapter_break
    target_segments: int
    
    # Agent results
    context_analysis: Optional[Dict[str, Any]]
    continuation_plan: Optional[Dict[str, Any]]
    narrative_segments: List[Dict[str, Any]]
    quality_checks: List[Dict[str, Any]]
    world_updates: Optional[Dict[str, Any]]
    visual_generations: List[Dict[str, Any]]
    
    # Workflow state
    current_segment: int
    completed_segments: List[Dict[str, Any]]
    current_step: str
    should_continue: bool
    chapter_complete: bool
    
    # Final output
    final_chapter_content: Optional[str]
    final_word_count: int
    continuation_context: Optional[Dict[str, Any]]
    
    # Error handling
    errors: List[str]
    warnings: List[str]

class ChapterContinuationWorkflow:
    """
    LangGraph-based workflow for seamless chapter continuation with unlimited content generation
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
            logger.info("Chapter continuation workflow initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize chapter continuation workflow: {e}")
            raise
    
    def _build_workflow_graph(self) -> StateGraph:
        """Build the LangGraph workflow for chapter continuation"""
        workflow = StateGraph(ChapterContinuationState)
        
        # Add nodes
        workflow.add_node("analyze_continuation_context", self._analyze_continuation_context)
        workflow.add_node("plan_continuation", self._plan_continuation)
        workflow.add_node("generate_segment", self._generate_segment)
        workflow.add_node("check_segment_quality", self._check_segment_quality)
        workflow.add_node("update_world_context", self._update_world_context)
        workflow.add_node("generate_segment_visuals", self._generate_segment_visuals)
        workflow.add_node("evaluate_continuation", self._evaluate_continuation)
        workflow.add_node("finalize_chapter", self._finalize_chapter)
        workflow.add_node("handle_continuation_error", self._handle_continuation_error)
        
        # Define workflow edges
        workflow.set_entry_point("analyze_continuation_context")
        
        # Main continuation flow
        workflow.add_edge("analyze_continuation_context", "plan_continuation")
        workflow.add_edge("plan_continuation", "generate_segment")
        workflow.add_edge("generate_segment", "check_segment_quality")
        
        # Quality check routing
        workflow.add_conditional_edges(
            "check_segment_quality",
            self._quality_routing,
            {
                "regenerate": "generate_segment",
                "update_world": "update_world_context",
                "continue": "evaluate_continuation",
                "error": "handle_continuation_error"
            }
        )
        
        # World update routing
        workflow.add_conditional_edges(
            "update_world_context",
            self._world_update_routing,
            {
                "generate_visuals": "generate_segment_visuals",
                "evaluate": "evaluate_continuation"
            }
        )
        
        # Visual generation routing
        workflow.add_edge("generate_segment_visuals", "evaluate_continuation")
        
        # Continuation evaluation routing
        workflow.add_conditional_edges(
            "evaluate_continuation",
            self._continuation_routing,
            {
                "continue_segment": "generate_segment",
                "finalize": "finalize_chapter",
                "error": "handle_continuation_error"
            }
        )
        
        # Error handling
        workflow.add_conditional_edges(
            "handle_continuation_error",
            self._error_routing,
            {
                "retry": "generate_segment",
                "finalize": "finalize_chapter",
                "end": END
            }
        )
        
        workflow.add_edge("finalize_chapter", END)
        
        return workflow.compile()
    
    async def execute_continuation_workflow(
        self,
        task_id: str,
        story_context: StoryContext,
        chapter_id: str,
        previous_content: str,
        user_direction: Optional[str] = None,
        continuation_mode: str = "seamless",
        target_segments: int = 5
    ) -> Dict[str, Any]:
        """
        Execute chapter continuation workflow
        
        Args:
            task_id: Unique task identifier
            story_context: Story context information
            chapter_id: ID of chapter being continued
            previous_content: Previous chapter content
            user_direction: Optional user direction for continuation
            continuation_mode: Mode of continuation
            target_segments: Target number of segments to generate
            
        Returns:
            Continuation result with new content
        """
        if not self.initialized:
            await self.initialize()
        
        # Initialize state
        initial_state = ChapterContinuationState(
            task_id=task_id,
            story_context=story_context.dict(),
            chapter_id=chapter_id,
            previous_content=previous_content,
            user_direction=user_direction,
            continuation_mode=continuation_mode,
            target_segments=target_segments,
            
            context_analysis=None,
            continuation_plan=None,
            narrative_segments=[],
            quality_checks=[],
            world_updates=None,
            visual_generations=[],
            
            current_segment=0,
            completed_segments=[],
            current_step="analyze_continuation_context",
            should_continue=True,
            chapter_complete=False,
            
            final_chapter_content=None,
            final_word_count=0,
            continuation_context=None,
            
            errors=[],
            warnings=[]
        )
        
        try:
            logger.info(f"Starting chapter continuation workflow for task {task_id}")
            
            final_state = await self.workflow.ainvoke(initial_state)
            
            return self._format_continuation_result(final_state)
            
        except Exception as e:
            logger.error(f"Chapter continuation workflow failed for task {task_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "task_id": task_id,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    # Workflow step implementations
    
    async def _analyze_continuation_context(self, state: ChapterContinuationState) -> ChapterContinuationState:
        """Analyze the context for chapter continuation"""
        try:
            logger.info(f"Analyzing continuation context for task {state['task_id']}")
            
            agent_context = AgentContext(
                agent_type=AgentType.CONTINUATION_CONTEXT,
                task_id=state["task_id"],
                story_context=StoryContext(**state["story_context"]),
                user_input=state.get("user_direction", ""),
                agent_specific_data={
                    "task_type": "create_continuation_context",
                    "content": state["previous_content"],
                    "chapter_id": state["chapter_id"]
                }
            )
            
            response = await self.agents['continuation_context'].process_request(agent_context)
            
            if response.success:
                state["context_analysis"] = response.result
                state["current_step"] = "plan_continuation"
            else:
                state["errors"].append(f"Context analysis failed: {response.error}")
                state["should_continue"] = False
            
            return state
            
        except Exception as e:
            logger.error(f"Context analysis failed: {e}")
            state["errors"].append(f"Context analysis error: {str(e)}")
            return state
    
    async def _plan_continuation(self, state: ChapterContinuationState) -> ChapterContinuationState:
        """Plan the chapter continuation strategy"""
        try:
            logger.info(f"Planning continuation for task {state['task_id']}")
            
            agent_context = AgentContext(
                agent_type=AgentType.CREATIVE_DIRECTOR,
                task_id=state["task_id"],
                story_context=StoryContext(**state["story_context"]),
                user_input=state.get("user_direction", ""),
                agent_specific_data={
                    "task_type": "plan_workflow",
                    "context_analysis": state["context_analysis"],
                    "continuation_mode": state["continuation_mode"],
                    "target_segments": state["target_segments"]
                }
            )
            
            response = await self.agents['creative_director'].process_request(agent_context)
            
            if response.success:
                state["continuation_plan"] = response.result
                state["current_step"] = "generate_segment"
            else:
                state["errors"].append(f"Continuation planning failed: {response.error}")
                state["should_continue"] = False
            
            return state
            
        except Exception as e:
            logger.error(f"Continuation planning failed: {e}")
            state["errors"].append(f"Planning error: {str(e)}")
            return state
    
    async def _generate_segment(self, state: ChapterContinuationState) -> ChapterContinuationState:
        """Generate a single narrative segment"""
        try:
            current_segment = state["current_segment"]
            logger.info(f"Generating segment {current_segment + 1} for task {state['task_id']}")
            
            # Prepare context for segment generation
            segment_context = {
                "previous_content": state["previous_content"],
                "completed_segments": state["completed_segments"],
                "continuation_plan": state["continuation_plan"],
                "context_analysis": state["context_analysis"]
            }
            
            agent_context = AgentContext(
                agent_type=AgentType.NARRATIVE_INTELLIGENCE,
                task_id=state["task_id"],
                story_context=StoryContext(**state["story_context"]),
                user_input=state.get("user_direction", ""),
                agent_specific_data={
                    "task_type": "generate_content",
                    "segment_number": current_segment + 1,
                    "segment_context": segment_context,
                    "target_word_count": 250  # Default segment length
                }
            )
            
            response = await self.agents['narrative_intelligence'].process_request(agent_context)
            
            if response.success:
                segment_result = response.result
                segment_result["segment_number"] = current_segment + 1
                state["narrative_segments"].append(segment_result)
                state["current_step"] = "check_segment_quality"
            else:
                state["errors"].append(f"Segment generation failed: {response.error}")
            
            return state
            
        except Exception as e:
            logger.error(f"Segment generation failed: {e}")
            state["errors"].append(f"Segment generation error: {str(e)}")
            return state
    
    async def _check_segment_quality(self, state: ChapterContinuationState) -> ChapterContinuationState:
        """Check quality of generated segment"""
        try:
            current_segment = state["current_segment"]
            logger.info(f"Checking quality of segment {current_segment + 1} for task {state['task_id']}")
            
            if not state["narrative_segments"]:
                state["errors"].append("No segment to check quality for")
                return state
            
            latest_segment = state["narrative_segments"][-1]
            segment_content = latest_segment.get("content", "")
            
            agent_context = AgentContext(
                agent_type=AgentType.QUALITY_ASSURANCE,
                task_id=state["task_id"],
                story_context=StoryContext(**state["story_context"]),
                user_input="",
                agent_specific_data={
                    "task_type": "full_quality_check",
                    "content": segment_content,
                    "segment_context": {
                        "segment_number": current_segment + 1,
                        "previous_content": state["previous_content"]
                    }
                }
            )
            
            response = await self.agents['quality_assurance'].process_request(agent_context)
            
            if response.success:
                quality_result = response.result
                quality_result["segment_number"] = current_segment + 1
                state["quality_checks"].append(quality_result)
                
                # Update segment with quality information
                latest_segment["quality_metrics"] = quality_result.get("quality_metrics", {})
                latest_segment["quality_passed"] = self._evaluate_segment_quality(quality_result)
                
                state["current_step"] = "update_world_context"
            else:
                state["warnings"].append(f"Quality check failed for segment {current_segment + 1}")
                state["current_step"] = "evaluate_continuation"
            
            return state
            
        except Exception as e:
            logger.warning(f"Quality check failed: {e}")
            state["warnings"].append(f"Quality check error: {str(e)}")
            state["current_step"] = "evaluate_continuation"
            return state
    
    async def _update_world_context(self, state: ChapterContinuationState) -> ChapterContinuationState:
        """Update world context based on segment content"""
        try:
            current_segment = state["current_segment"]
            logger.info(f"Updating world context for segment {current_segment + 1}")
            
            if not state["narrative_segments"]:
                return state
            
            latest_segment = state["narrative_segments"][-1]
            segment_content = latest_segment.get("content", "")
            
            agent_context = AgentContext(
                agent_type=AgentType.WORLD_BUILDING,
                task_id=state["task_id"],
                story_context=StoryContext(**state["story_context"]),
                user_input="",
                agent_specific_data={
                    "task_type": "enhance_setting",
                    "content": segment_content,
                    "segment_context": True
                }
            )
            
            response = await self.agents['world_building'].process_request(agent_context)
            
            if response.success:
                if not state["world_updates"]:
                    state["world_updates"] = {"segment_updates": []}
                
                world_result = response.result
                world_result["segment_number"] = current_segment + 1
                state["world_updates"]["segment_updates"].append(world_result)
            
            state["current_step"] = "evaluate_continuation"
            return state
            
        except Exception as e:
            logger.warning(f"World context update failed: {e}")
            state["warnings"].append(f"World update error: {str(e)}")
            state["current_step"] = "evaluate_continuation"
            return state
    
    async def _generate_segment_visuals(self, state: ChapterContinuationState) -> ChapterContinuationState:
        """Generate visuals for segment if needed"""
        try:
            current_segment = state["current_segment"]
            logger.info(f"Generating visuals for segment {current_segment + 1}")
            
            # Check if images are enabled in story context
            story_context = StoryContext(**state["story_context"])
            if not story_context.image_settings.get("enabled", False):
                return state
            
            if not state["narrative_segments"]:
                return state
            
            latest_segment = state["narrative_segments"][-1]
            segment_content = latest_segment.get("content", "")
            
            agent_context = AgentContext(
                agent_type=AgentType.VISUAL_STORYTELLING,
                task_id=state["task_id"],
                story_context=story_context,
                user_input="",
                agent_specific_data={
                    "task_type": "analyze_visual_opportunities",
                    "content": segment_content
                }
            )
            
            response = await self.agents['visual_storytelling'].process_request(agent_context)
            
            if response.success:
                visual_result = response.result
                visual_result["segment_number"] = current_segment + 1
                state["visual_generations"].append(visual_result)
            
            return state
            
        except Exception as e:
            logger.warning(f"Visual generation failed: {e}")
            state["warnings"].append(f"Visual generation error: {str(e)}")
            return state
    
    async def _evaluate_continuation(self, state: ChapterContinuationState) -> ChapterContinuationState:
        """Evaluate if continuation should continue or stop"""
        try:
            current_segment = state["current_segment"]
            logger.info(f"Evaluating continuation after segment {current_segment + 1}")
            
            # Mark current segment as completed
            if state["narrative_segments"]:
                latest_segment = state["narrative_segments"][-1]
                state["completed_segments"].append(latest_segment)
            
            # Increment segment counter
            state["current_segment"] += 1
            
            # Determine if we should continue
            should_continue = self._should_continue_generation(state)
            
            if should_continue:
                state["current_step"] = "generate_segment"
                state["should_continue"] = True
            else:
                state["current_step"] = "finalize_chapter"
                state["should_continue"] = False
                state["chapter_complete"] = True
            
            return state
            
        except Exception as e:
            logger.error(f"Continuation evaluation failed: {e}")
            state["errors"].append(f"Evaluation error: {str(e)}")
            state["current_step"] = "finalize_chapter"
            return state
    
    async def _finalize_chapter(self, state: ChapterContinuationState) -> ChapterContinuationState:
        """Finalize chapter content and create continuation context"""
        try:
            logger.info(f"Finalizing chapter for task {state['task_id']}")
            
            # Combine all segments into final content
            all_content = [state["previous_content"]]
            total_word_count = len(state["previous_content"].split()) if state["previous_content"] else 0
            
            for segment in state["completed_segments"]:
                segment_content = segment.get("content", "")
                all_content.append(segment_content)
                total_word_count += segment.get("word_count", 0)
            
            # Join content with appropriate spacing
            final_content = "\n\n".join(filter(None, all_content))
            
            # Create final continuation context
            agent_context = AgentContext(
                agent_type=AgentType.CONTINUATION_CONTEXT,
                task_id=state["task_id"],
                story_context=StoryContext(**state["story_context"]),
                user_input="",
                agent_specific_data={
                    "task_type": "create_continuation_context",
                    "content": final_content[-2000:],  # Last 2000 chars for context
                    "chapter_id": state["chapter_id"]
                }
            )
            
            response = await self.agents['continuation_context'].process_request(agent_context)
            
            if response.success:
                state["continuation_context"] = response.result
            
            # Set final results
            state["final_chapter_content"] = final_content
            state["final_word_count"] = total_word_count
            
            logger.info(f"Chapter finalized with {len(state['completed_segments'])} segments, {total_word_count} words")
            
            return state
            
        except Exception as e:
            logger.error(f"Chapter finalization failed: {e}")
            state["errors"].append(f"Finalization error: {str(e)}")
            return state
    
    async def _handle_continuation_error(self, state: ChapterContinuationState) -> ChapterContinuationState:
        """Handle errors in continuation workflow"""
        logger.warning(f"Handling continuation errors for task {state['task_id']}: {state['errors']}")
        
        # For now, just proceed to finalization with whatever we have
        state["current_step"] = "finalize_chapter"
        state["should_continue"] = False
        
        return state
    
    # Utility methods
    
    def _evaluate_segment_quality(self, quality_result: Dict[str, Any]) -> bool:
        """Evaluate if segment quality is acceptable"""
        quality_metrics = quality_result.get("quality_metrics", {})
        overall_score = quality_metrics.get("overall_quality_score", 0.5)
        
        return overall_score >= 0.7  # Minimum acceptable quality
    
    def _should_continue_generation(self, state: ChapterContinuationState) -> bool:
        """Determine if generation should continue"""
        current_segment = state["current_segment"]
        target_segments = state["target_segments"]
        
        # Check if we've reached target segments
        if current_segment >= target_segments:
            return False
        
        # Check for too many errors
        if len(state["errors"]) > 3:
            return False
        
        # Check continuation mode
        if state["continuation_mode"] == "user_guided":
            # In user-guided mode, stop after each segment for user input
            return False
        
        return True
    
    def _format_continuation_result(self, final_state: ChapterContinuationState) -> Dict[str, Any]:
        """Format final continuation result"""
        return {
            "success": len(final_state["errors"]) == 0,
            "task_id": final_state["task_id"],
            "chapter_id": final_state["chapter_id"],
            "content": final_state.get("final_chapter_content", ""),
            "word_count": final_state.get("final_word_count", 0),
            "segments_generated": len(final_state["completed_segments"]),
            "continuation_context": final_state.get("continuation_context", {}),
            "quality_checks": final_state["quality_checks"],
            "world_updates": final_state.get("world_updates", {}),
            "visual_generations": final_state["visual_generations"],
            "errors": final_state["errors"],
            "warnings": final_state["warnings"],
            "timestamp": datetime.utcnow().isoformat(),
            "generation_metadata": {
                "continuation_mode": final_state["continuation_mode"],
                "target_segments": final_state["target_segments"],
                "actual_segments": len(final_state["completed_segments"]),
                "chapter_complete": final_state.get("chapter_complete", False)
            }
        }
    
    # Conditional routing functions
    
    def _quality_routing(self, state: ChapterContinuationState) -> str:
        """Route based on quality check results"""
        if not state["quality_checks"]:
            return "error"
        
        latest_quality = state["quality_checks"][-1]
        
        if not self._evaluate_segment_quality(latest_quality):
            # Quality too low, try regenerating once
            current_segment = state["current_segment"]
            regeneration_count = sum(1 for q in state["quality_checks"] 
                                   if q.get("segment_number") == current_segment + 1)
            
            if regeneration_count < 2:  # Allow one regeneration
                return "regenerate"
            else:
                return "continue"  # Accept lower quality after retry
        
        return "update_world"
    
    def _world_update_routing(self, state: ChapterContinuationState) -> str:
        """Route after world update"""
        story_context = StoryContext(**state["story_context"])
        
        if story_context.image_settings.get("enabled", False):
            return "generate_visuals"
        else:
            return "evaluate"
    
    def _continuation_routing(self, state: ChapterContinuationState) -> str:
        """Route continuation decision"""
        if state.get("should_continue", False):
            return "continue_segment"
        else:
            return "finalize"
    
    def _error_routing(self, state: ChapterContinuationState) -> str:
        """Route error handling"""
        if len(state["errors"]) > 5:
            return "end"
        elif state.get("completed_segments"):
            return "finalize"
        else:
            return "retry"

# Global workflow instance
chapter_workflow = ChapterContinuationWorkflow()

# Convenience function
async def execute_chapter_continuation(
    task_id: str,
    story_context: StoryContext,
    chapter_id: str,
    previous_content: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Execute chapter continuation workflow
    
    Args:
        task_id: Unique task identifier
        story_context: Story context information
        chapter_id: Chapter being continued
        previous_content: Previous chapter content
        **kwargs: Additional workflow parameters
        
    Returns:
        Continuation result
    """
    if not chapter_workflow.initialized:
        await chapter_workflow.initialize()
    
    return await chapter_workflow.execute_continuation_workflow(
        task_id=task_id,
        story_context=story_context,
        chapter_id=chapter_id,
        previous_content=previous_content,
        **kwargs
    )
