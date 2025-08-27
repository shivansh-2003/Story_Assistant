# services/llm_service.py
import asyncio
import logging
import json
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import tiktoken
import httpx

from config.settings import settings, LLM_CONFIGS, AGENT_CONFIGS

logger = logging.getLogger(__name__)

class LLMService:
    """
    Groq-only LLM service with token management and cost optimization.
    Essential features for Story Assistant story generation.
    """
    
    def __init__(self):
        self.groq_client = None
        self.initialized = False
        self.token_encoder = None
        self.generation_history: List[Dict[str, Any]] = []
        
        # Initialize token encoder
        try:
            self.token_encoder = tiktoken.get_encoding("cl100k_base")
        except Exception as e:
            logger.warning(f"Could not initialize token encoder: {e}")
    
    async def initialize(self):
        """Initialize Groq client"""
        try:
            # Check if Groq API key is available
            if not hasattr(settings, 'groq_api_key') or not settings.groq_api_key:
                raise Exception("Groq API key not found. Please set GROQ_API_KEY in your environment.")
            
            # Initialize Groq client
            self.groq_client = httpx.AsyncClient(
                base_url="https://api.groq.com/openai/v1",
                headers={
                    "Authorization": f"Bearer {settings.groq_api_key}",
                    "Content-Type": "application/json"
                },
                timeout=60.0
            )
            
            # Test connection
            await self._test_connection()
            
            self.initialized = True
            logger.info("Groq LLM service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Groq LLM service: {e}")
            raise
    
    async def _test_connection(self):
        """Test Groq API connection"""
        try:
            # Simple test request
            test_response = await self.groq_client.post(
                "/chat/completions",
                json={
                    "model": "llama3-70b-8192",
                    "messages": [{"role": "user", "content": "Hello, please respond with 'OK'"}],
                    "max_tokens": 10,
                    "temperature": 0.1
                }
            )
            
            if test_response.status_code == 200:
                response_data = test_response.json()
                if "OK" in response_data.get("choices", [{}])[0].get("message", {}).get("content", ""):
                    logger.info("Groq API connection test successful")
                else:
                    raise Exception("Unexpected response from Groq API")
            else:
                raise Exception(f"Groq API test failed with status {test_response.status_code}")
                
        except Exception as e:
            logger.error(f"Groq API connection test failed: {e}")
            raise
    
    async def generate_content(
        self,
        prompt: str,
        agent_type: str = "general",
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        system_message: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate content using Groq LLM
        
        Args:
            prompt: User prompt
            agent_type: Type of agent (creative_director, narrative_intelligence, etc.)
            max_tokens: Maximum tokens to generate
            temperature: Creativity level (0.0-1.0)
            system_message: System instruction
            **kwargs: Additional parameters
            
        Returns:
            Dictionary with generation results
        """
        if not self.initialized:
            await self.initialize()
        
        try:
            # Get agent-specific configuration
            agent_config = AGENT_CONFIGS.get(agent_type, AGENT_CONFIGS["narrative_intelligence"])
            
            # Set parameters
            max_tokens = max_tokens or agent_config.get("max_tokens", 2000)
            temperature = temperature or agent_config.get("temperature", 0.7)
            
            # Prepare messages
            messages = []
            if system_message:
                messages.append({"role": "system", "content": system_message})
            messages.append({"role": "user", "content": prompt})
            
            # Count input tokens
            input_tokens = self._count_tokens(prompt)
            if system_message:
                input_tokens += self._count_tokens(system_message)
            
            # Make API request
            start_time = datetime.utcnow()
            
            response = await self.groq_client.post(
                "/chat/completions",
                json={
                    "model": "llama3-70b-8192",
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "stream": False,
                    **kwargs
                }
            )
            
            if response.status_code != 200:
                raise Exception(f"Groq API request failed: {response.status_code} - {response.text}")
            
            response_data = response.json()
            content = response_data["choices"][0]["message"]["content"]
            output_tokens = response_data["usage"]["completion_tokens"]
            total_tokens = response_data["usage"]["total_tokens"]
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Calculate cost (Groq pricing: $0.20 per 1M input tokens, $0.80 per 1M output tokens)
            input_cost = (input_tokens / 1_000_000) * 0.20
            output_cost = (output_tokens / 1_000_000) * 0.80
            total_cost = input_cost + output_cost
            
            # Store generation history
            generation_record = {
                "timestamp": datetime.utcnow().isoformat(),
                "agent_type": agent_type,
                "prompt": prompt,
                "response": content,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": total_tokens,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "execution_time": execution_time,
                "cost": total_cost,
                "provider": "groq",
                "model": "llama3-70b-8192"
            }
            self.generation_history.append(generation_record)
            
            # Keep only last 100 generations
            if len(self.generation_history) > 100:
                self.generation_history = self.generation_history[-100:]
            
            return {
                "success": True,
                "content": content,
                "provider": "groq",
                "model": "llama3-70b-8192",
                "agent_type": agent_type,
                "tokens": {
                    "input": input_tokens,
                    "output": output_tokens,
                    "total": total_tokens
                },
                "cost": total_cost,
                "execution_time": execution_time,
                "metadata": {
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "generated_at": datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Content generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "provider": "groq",
                "agent_type": agent_type
            }
    
    def _count_tokens(self, text: str) -> int:
        """Count tokens in text using tiktoken"""
        if not self.token_encoder:
            # Rough estimation (1 token ≈ 4 characters)
            return len(text) // 4
        
        try:
            return len(self.token_encoder.encode(text))
        except Exception as e:
            logger.warning(f"Token counting failed: {e}")
            # Rough estimation
            return len(text) // 4
    
    async def generate_with_retry(
        self,
        prompt: str,
        agent_type: str = "general",
        max_retries: int = 3,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate content with retry logic
        
        Args:
            prompt: User prompt
            agent_type: Type of agent
            max_retries: Maximum retry attempts
            **kwargs: Additional generation parameters
            
        Returns:
            Dictionary with generation results
        """
        for attempt in range(max_retries):
            try:
                result = await self.generate_content(prompt, agent_type, **kwargs)
                if result["success"]:
                    return result
                
                # If failed, wait before retry
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.warning(f"Generation failed, retrying in {wait_time}s... (attempt {attempt + 1}/{max_retries})")
                    await asyncio.sleep(wait_time)
                    
            except Exception as e:
                logger.error(f"Generation attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    return {
                        "success": False,
                        "error": f"All {max_retries} attempts failed. Last error: {str(e)}",
                        "provider": "groq",
                        "agent_type": agent_type
                    }
        
        return {
            "success": False,
            "error": "Max retries exceeded",
            "provider": "groq",
            "agent_type": agent_type
        }
    
    async def batch_generate(
        self,
        prompts: List[str],
        agent_type: str = "general",
        max_concurrent: int = 5,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Generate content for multiple prompts concurrently
        
        Args:
            prompts: List of prompts
            agent_type: Type of agent
            max_concurrent: Maximum concurrent requests
            **kwargs: Additional generation parameters
            
        Returns:
            List of generation results
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def generate_single(prompt: str) -> Dict[str, Any]:
            async with semaphore:
                return await self.generate_content(prompt, agent_type, **kwargs)
        
        # Create tasks for all prompts
        tasks = [generate_single(prompt) for prompt in prompts]
        
        # Execute concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    "success": False,
                    "error": str(result),
                    "prompt": prompts[i],
                    "provider": "groq",
                    "agent_type": agent_type
                })
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of Groq LLM service"""
        
        health_status = {
            "service_status": "healthy",
            "provider": "groq",
            "initialized": self.initialized,
            "model": "llama3-70b-8192"
        }
        
        if not self.initialized:
            health_status["service_status"] = "uninitialized"
            return health_status
        
        try:
            # Test with simple generation
            test_result = await self.generate_content(
                "Health check - respond with 'OK'",
                agent_type="general",
                max_tokens=5,
                temperature=0.1
            )
            
            if test_result["success"] and "OK" in test_result["content"]:
                health_status["service_status"] = "healthy"
                health_status["response_time"] = test_result.get("execution_time", 0)
            else:
                health_status["service_status"] = "degraded"
                health_status["error"] = test_result.get("error", "Unexpected response")
                
        except Exception as e:
            health_status["service_status"] = "unhealthy"
            health_status["error"] = str(e)
        
        return health_status
    
    def get_generation_stats(self) -> Dict[str, Any]:
        """Get generation statistics"""
        if not self.generation_history:
            return {
                "total_generations": 0,
                "total_tokens": 0,
                "total_cost": 0.0,
                "average_execution_time": 0.0
            }
        
        total_generations = len(self.generation_history)
        total_tokens = sum(gen.get("total_tokens", 0) for gen in self.generation_history)
        total_cost = sum(gen.get("cost", 0.0) for gen in self.generation_history)
        avg_execution_time = sum(gen.get("execution_time", 0.0) for gen in self.generation_history) / total_generations
        
        return {
            "total_generations": total_generations,
            "total_tokens": total_tokens,
            "total_cost": total_cost,
            "average_execution_time": avg_execution_time,
            "recent_generations": len([gen for gen in self.generation_history if self._is_recent(gen)]),
            "provider": "groq",
            "model": "llama3-70b-8192"
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
        if self.groq_client:
            await self.groq_client.aclose()
            self.groq_client = None
        self.initialized = False

# Global Groq LLM service instance
llm_service = LLMService()

# Convenience function
async def get_llm_service() -> LLMService:
    """Get initialized Groq LLM service instance"""
    if not llm_service.initialized:
        await llm_service.initialize()
    return llm_service
