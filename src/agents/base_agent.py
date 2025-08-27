# agents/base_agent.py
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_community.llms import Ollama
import json
import time
import uuid
from datetime import datetime
import logging

from models.generation_models import (
    AgentContext, AgentResponse, StoryContext, 
    AgentType, QualityMetrics
)
from config.settings import settings, AGENT_CONFIGS, LLM_CONFIGS
from services.vector_service import VectorService

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """
    Base class for all Story Assistant agents.
    Provides common functionality for LLM interaction, context management,
    and communication with other agents.
    """
    
    def __init__(
        self, 
        agent_type: AgentType,
        vector_service: VectorService,
        primary_llm: Optional[str] = None,
        fallback_llm: Optional[str] = None
    ):
        self.agent_type = agent_type
        self.agent_id = f"{agent_type.value}_{uuid.uuid4().hex[:8]}"
        self.vector_service = vector_service
        
        # Get agent-specific configuration
        self.config = AGENT_CONFIGS.get(agent_type.value, {})
        
        # Initialize LLM
        self.primary_llm_name = primary_llm or self.config.get("primary_llm", "groq")
        
        self.primary_llm = self._initialize_llm(self.primary_llm_name)
        self.current_llm = self.primary_llm
        
        # Agent state
        self.execution_history: List[Dict[str, Any]] = []
        self.performance_metrics: Dict[str, float] = {}
        
        logger.info(f"Initialized {self.agent_type.value} agent with ID: {self.agent_id}")
    
    def _initialize_llm(self, llm_name: str) -> BaseLanguageModel:
        """Initialize language model based on configuration"""
        llm_config = LLM_CONFIGS.get(llm_name, {})
        
        try:
            if llm_name == "openai":
                if not settings.openai_api_key:
                    raise ValueError("OpenAI API key not configured")
                return ChatOpenAI(
                    model=llm_config.get("model", "gpt-4-turbo-preview"),
                    temperature=llm_config.get("temperature", 0.7),
                    max_tokens=llm_config.get("max_tokens", 2000),
                    api_key=settings.openai_api_key
                )
            
            elif llm_name == "anthropic":
                if not settings.anthropic_api_key:
                    raise ValueError("Anthropic API key not configured")
                return ChatAnthropic(
                    model=llm_config.get("model", "claude-3-sonnet-20240229"),
                    temperature=llm_config.get("temperature", 0.7),
                    max_tokens=llm_config.get("max_tokens", 2000),
                    api_key=settings.anthropic_api_key
                )
            
            elif llm_name == "groq":
                if not settings.groq_api_key:
                    raise ValueError("Groq API key not configured")
                # Use httpx client for Groq API calls
                return None  # Will be handled by LLM service
            
            else:
                raise ValueError(f"Unknown LLM: {llm_name}")
                
        except Exception as e:
            logger.error(f"Failed to initialize {llm_name}: {e}")
            raise
    
    async def process_request(self, context: AgentContext) -> AgentResponse:
        """
        Main entry point for processing agent requests.
        Handles error management and fallback strategies.
        """
        start_time = time.time()
        
        try:
            # Validate input
            self._validate_context(context)
            
            # Execute agent-specific logic
            result = await self._execute_task(context)
            
            # Record successful execution
            execution_time = int((time.time() - start_time) * 1000)
            self._record_execution(context, result, execution_time, success=True)
            
            return AgentResponse(
                agent_id=self.agent_id,
                task_id=context.task_id,
                success=True,
                result=result,
                execution_time_ms=execution_time,
                next_agents=self._get_next_agents(context, result)
            )
            
        except Exception as e:
            logger.error(f"Agent {self.agent_id} failed: {e}")
            
            # Record failed execution
            execution_time = int((time.time() - start_time) * 1000)
            self._record_execution(context, None, execution_time, success=False, error=str(e))
            
            return AgentResponse(
                agent_id=self.agent_id,
                task_id=context.task_id,
                success=False,
                error=str(e),
                execution_time_ms=execution_time
            )
    
    @abstractmethod
    async def _execute_task(self, context: AgentContext) -> Dict[str, Any]:
        """
        Agent-specific task execution logic.
        Must be implemented by each agent subclass.
        """
        pass
    
    def _validate_context(self, context: AgentContext) -> None:
        """Validate agent context before processing"""
        if not context.story_context.story_id:
            raise ValueError("Story ID is required")
        
        # Agent-specific validation can be overridden
        self._validate_agent_specific_context(context)
    
    def _validate_agent_specific_context(self, context: AgentContext) -> None:
        """Override in subclasses for agent-specific validation"""
        pass
    
    async def _get_relevant_context(
        self, 
        story_context: StoryContext, 
        query: str,
        context_type: str = "general",
        max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant context from vector database using semantic search
        """
        try:
            collection_name = self._get_collection_name(context_type)
            
            relevant_docs = await self.vector_service.search_similar(
                collection_name=collection_name,
                query_text=query,
                filter_metadata={"story_id": str(story_context.story_id)},
                n_results=max_results
            )
            
            return relevant_docs
            
        except Exception as e:
            logger.warning(f"Failed to retrieve context: {e}")
            return []
    
    def _get_collection_name(self, context_type: str) -> str:
        """Map context type to vector collection name"""
        collection_mapping = {
            "character": "character_embeddings",
            "plot": "plot_embeddings",
            "world": "world_embeddings",
            "dialogue": "dialogue_embeddings",
            "general": "context_embeddings"
        }
        return collection_mapping.get(context_type, "context_embeddings")
    
    async def _generate_with_llm(
        self, 
        prompt: Union[str, ChatPromptTemplate], 
        context_vars: Dict[str, Any],
        output_parser: Optional[Any] = None,
        max_retries: int = 2
    ) -> Union[str, Dict[str, Any]]:
        """
        Generate content using current LLM with error handling and retries
        """
        if output_parser is None:
            output_parser = StrOutputParser()
        
        for attempt in range(max_retries + 1):
            try:
                if isinstance(prompt, str):
                    prompt_template = PromptTemplate.from_template(prompt)
                    chain = prompt_template | self.current_llm | output_parser
                else:
                    chain = prompt | self.current_llm | output_parser
                
                result = await chain.ainvoke(context_vars)
                return result
                
            except Exception as e:
                logger.warning(f"LLM generation attempt {attempt + 1} failed: {e}")
                if attempt < max_retries:
                    time.sleep(1)  # Brief delay before retry
                else:
                    raise
    
    def _create_agent_prompt(self, base_prompt: str, context: AgentContext) -> ChatPromptTemplate:
        """
        Create a comprehensive prompt with agent context
        """
        system_prompt = f"""
        You are a {self.agent_type.value.replace('_', ' ').title()} for an AI Story Assistant.
        
        Your specific role and responsibilities:
        {self._get_agent_role_description()}
        
        Current story context:
        - Story ID: {context.story_context.story_id}
        - Genre: {context.story_context.story_metadata.get('genre', 'Unknown')}
        - Writing Style: {context.story_context.story_metadata.get('writing_style', 'Unknown')}
        - Target Audience: {context.story_context.story_metadata.get('target_audience', 'Unknown')}
        
        Generation Settings:
        {json.dumps(context.story_context.generation_settings, indent=2)}
        
        Always maintain consistency with:
        1. Previously established characters and their traits
        2. World-building elements and rules
        3. Plot threads and narrative continuity
        4. Writing style and tone
        5. Genre conventions and target audience expectations
        
        {base_prompt}
        """
        
        return ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{user_input}")
        ])
    
    @abstractmethod
    def _get_agent_role_description(self) -> str:
        """
        Return a description of this agent's specific role and capabilities.
        Must be implemented by each agent subclass.
        """
        pass
    
    def _get_next_agents(self, context: AgentContext, result: Dict[str, Any]) -> List[str]:
        """
        Determine which agents should be called next based on current results.
        Can be overridden by subclasses for agent-specific flow control.
        """
        return []
    
    def _record_execution(
        self, 
        context: AgentContext, 
        result: Optional[Dict[str, Any]], 
        execution_time_ms: int,
        success: bool,
        error: Optional[str] = None
    ) -> None:
        """Record execution for performance monitoring and learning"""
        execution_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "task_id": context.task_id,
            "story_id": str(context.story_context.story_id),
            "execution_time_ms": execution_time_ms,
            "success": success,
            "error": error,
            "llm_used": self.current_llm.__class__.__name__,
            "result_size": len(str(result)) if result else 0
        }
        
        self.execution_history.append(execution_record)
        
        # Update performance metrics
        self._update_performance_metrics(execution_record)
    
    def _update_performance_metrics(self, execution_record: Dict[str, Any]) -> None:
        """Update agent performance metrics"""
        # Calculate moving averages
        recent_executions = self.execution_history[-10:]  # Last 10 executions
        
        if recent_executions:
            self.performance_metrics.update({
                "avg_execution_time_ms": sum(e["execution_time_ms"] for e in recent_executions) / len(recent_executions),
                "success_rate": sum(1 for e in recent_executions if e["success"]) / len(recent_executions),
                "total_executions": len(self.execution_history)
            })
    
    async def _store_result_in_vector_db(
        self, 
        content: str, 
        metadata: Dict[str, Any],
        collection_name: str
    ) -> str:
        """Store generated content in vector database for future retrieval"""
        try:
            embedding_id = await self.vector_service.store_embedding(
                collection_name=collection_name,
                text=content,
                metadata=metadata
            )
            return embedding_id
        except Exception as e:
            logger.warning(f"Failed to store result in vector DB: {e}")
            return ""
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get agent performance summary"""
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type.value,
            "performance_metrics": self.performance_metrics,
            "total_executions": len(self.execution_history),
            "recent_errors": [
                e for e in self.execution_history[-5:] 
                if not e["success"]
            ]
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform agent health check"""
        try:
            # Test LLM connectivity
            test_result = await self._generate_with_llm(
                "Respond with 'OK' if you can see this message.",
                {},
                max_retries=1
            )
            
            llm_healthy = "OK" in str(test_result)
            
            return {
                "agent_id": self.agent_id,
                "agent_type": self.agent_type.value,
                "status": "healthy" if llm_healthy else "unhealthy",
                "llm_connectivity": llm_healthy,
                "vector_service": await self.vector_service.health_check(),
                "performance_metrics": self.performance_metrics
            }
            
        except Exception as e:
            return {
                "agent_id": self.agent_id,
                "agent_type": self.agent_type.value,
                "status": "unhealthy",
                "error": str(e)
            }
