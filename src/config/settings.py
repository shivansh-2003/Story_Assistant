# config/settings.py
from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application
    app_name: str = "Story Assistant"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    secret_key: str
    
    # Supabase
    supabase_url: str
    supabase_anon_key: str
    supabase_service_role_key: str
    
    # Database
    database_url: str
    
    # LLM APIs (Groq only for LLM operations)
    groq_api_key: str  # Required for LLM operations
    
    # OpenAI (for embeddings)
    openai_api_key: str  # Required for embeddings
    
    # Gemini Vision (for image analysis and guidance)
    gemini_api_key: Optional[str] = None
    
    # Pinecone Vector Database
    pinecone_api_key: str  # Required for vector database
    pinecone_environment: str  # e.g., "us-west1-gcp"
    pinecone_index_name: str = "story-assistant-index"
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # Generation Settings
    default_max_tokens: int = 2000
    default_temperature: float = 0.7
    max_concurrent_generations: int = 10
    
    # Vector DB Settings (OpenAI embeddings)
    embedding_model: str = "text-embedding-ada-002"
    vector_dimension: int = 1536  # OpenAI text-embedding-ada-002 dimension
    similarity_threshold: float = 0.8
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()

# LLM Configuration (Groq only)
LLM_CONFIGS = {
    "groq": {
        "model": "llama3-70b-8192",
        "max_tokens": 2000,
        "temperature": 0.7,
    }
}

# Agent Configurations (All using Groq)
AGENT_CONFIGS = {
    "creative_director": {
        "primary_llm": "groq",
        "max_tokens": 1000,
        "temperature": 0.5,
    },
    "narrative_intelligence": {
        "primary_llm": "groq",
        "max_tokens": 3000,
        "temperature": 0.8,
    },
    "quality_assurance": {
        "primary_llm": "groq",
        "max_tokens": 1500,
        "temperature": 0.3,
    },
    "world_building": {
        "primary_llm": "groq",
        "max_tokens": 2000,
        "temperature": 0.7,
    },
    "visual_storytelling": {
        "primary_llm": "groq",
        "max_tokens": 500,
        "temperature": 0.6,
    },
    "continuation_context": {
        "primary_llm": "groq",
        "max_tokens": 1000,
        "temperature": 0.4,
    },
    "gemini_vision": {
        "primary_llm": "groq",  # Groq for text operations
        "max_tokens": 1500,
        "temperature": 0.5,
    }
}

# Vector Database Collections
VECTOR_COLLECTIONS = {
    "character_descriptions": "character_embeddings",
    "plot_points": "plot_embeddings",
    "world_building": "world_embeddings",
    "dialogue_patterns": "dialogue_embeddings",
    "story_contexts": "context_embeddings",
    "generation_history": "generation_embeddings"
}

# Gemini Vision Settings
IMAGE_GENERATION_CONFIGS = {
    "gemini_vision": {
        "model": "gemini-1.5-flash",
        "analysis_depth": "detailed",
        "visual_guidance": "comprehensive",

    }
}
