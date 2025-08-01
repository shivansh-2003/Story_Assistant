from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Optional
from models import Character, StoryTheme, StorySegment
from llm_service import llm_service
import json

class StoryState(TypedDict):
    story_id: str
    theme: StoryTheme
    characters: List[Character]
    previous_content: str
    user_choice: Optional[str]
    auto_continue: bool
    current_segment: Optional[str]
    edit_instruction: Optional[str]
    context: Optional[str]
    workflow_type: str  # "generate" or "edit"

class StoryWorkflow:
    def __init__(self):
        self.workflow = self._build_workflow()
    
    def _build_workflow(self):
        workflow = StateGraph(StoryState)
        
        # Add nodes
        workflow.add_node("validate_input", self._validate_input)
        workflow.add_node("generate_content", self._generate_content)
        workflow.add_node("edit_content", self._edit_content)
        workflow.add_node("finalize_output", self._finalize_output)
        
        # Add edges
        workflow.add_conditional_edges(
            "validate_input",
            self._route_workflow,
            {
                "generate": "generate_content",
                "edit": "edit_content"
            }
        )
        workflow.add_edge("generate_content", "finalize_output")
        workflow.add_edge("edit_content", "finalize_output")
        workflow.add_edge("finalize_output", END)
        
        workflow.set_entry_point("validate_input")
        
        return workflow.compile()
    
    def _validate_input(self, state: StoryState) -> StoryState:
        """Validate input parameters"""
        if not state.get("story_id"):
            raise ValueError("Story ID is required")
        
        if state.get("workflow_type") == "generate":
            if not state.get("previous_content"):
                raise ValueError("Previous content is required for generation")
        elif state.get("workflow_type") == "edit":
            if not state.get("edit_instruction") or not state.get("current_segment"):
                raise ValueError("Edit instruction and current segment are required")
        
        return state
    
    def _route_workflow(self, state: StoryState) -> str:
        """Route to appropriate workflow based on type"""
        return state.get("workflow_type", "generate")
    
    def _generate_content(self, state: StoryState) -> StoryState:
        """Generate new story content"""
        try:
            new_content = llm_service.generate_story_continuation(
                theme=state["theme"],
                characters=state["characters"],
                previous_content=state["previous_content"],
                user_choice=state.get("user_choice"),
                auto_continue=state.get("auto_continue", False)
            )
            state["current_segment"] = new_content
            state["success"] = True
        except Exception as e:
            state["error"] = str(e)
            state["success"] = False
        
        return state
    
    def _edit_content(self, state: StoryState) -> StoryState:
        """Edit existing story content"""
        try:
            edited_content = llm_service.edit_story_segment(
                original_content=state["current_segment"],
                edit_instruction=state["edit_instruction"],
                context=state.get("context", ""),
                characters=state["characters"]
            )
            state["edited_content"] = edited_content
            state["success"] = True
        except Exception as e:
            state["error"] = str(e)
            state["success"] = False
        
        return state
    
    def _finalize_output(self, state: StoryState) -> StoryState:
        """Finalize the output"""
        if not state.get("success"):
            state["message"] = f"Workflow failed: {state.get('error', 'Unknown error')}"
        else:
            if state.get("workflow_type") == "generate":
                state["message"] = "Story content generated successfully"
            else:
                state["message"] = "Content edited successfully"
        
        return state
    
    def generate_story_segment(self,
                             story_id: str,
                             theme: StoryTheme,
                             characters: List[Character],
                             previous_content: str,
                             user_choice: str = None,
                             auto_continue: bool = False) -> dict:
        """Generate new story segment using workflow"""
        
        initial_state = StoryState(
            story_id=story_id,
            theme=theme,
            characters=characters,
            previous_content=previous_content,
            user_choice=user_choice,
            auto_continue=auto_continue,
            workflow_type="generate"
        )
        
        result = self.workflow.invoke(initial_state)
        
        return {
            "success": result.get("success", False),
            "content": result.get("current_segment", ""),
            "message": result.get("message", ""),
            "error": result.get("error")
        }
    
    def edit_story_segment(self,
                          story_id: str,
                          current_segment: str,
                          edit_instruction: str,
                          context: str = "",
                          characters: List[Character] = None) -> dict:
        """Edit story segment using workflow"""
        
        initial_state = StoryState(
            story_id=story_id,
            current_segment=current_segment,
            edit_instruction=edit_instruction,
            context=context,
            characters=characters or [],
            workflow_type="edit",
            theme=StoryTheme.FANTASY,  # Default, not used in editing
            previous_content=""  # Not used in editing
        )
        
        result = self.workflow.invoke(initial_state)
        
        return {
            "success": result.get("success", False),
            "original_content": current_segment,
            "edited_content": result.get("edited_content", ""),
            "message": result.get("message", ""),
            "error": result.get("error")
        }

# Global workflow instance
story_workflow = StoryWorkflow()