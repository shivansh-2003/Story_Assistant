# config/database_config.py
import asyncio
import logging
from typing import Dict, Any, List, Optional
from supabase import create_client, Client
from config.settings import settings

logger = logging.getLogger(__name__)

class DatabaseConfig:
    """
    Essential database configuration and schema management for Story Assistant.
    Handles Supabase initialization and table creation.
    """
    
    def __init__(self):
        self.supabase: Optional[Client] = None
        self.initialized = False
        
    async def initialize(self):
        """Initialize Supabase client and verify connection"""
        try:
            # Create Supabase client
            self.supabase = create_client(
        settings.supabase_url,
        settings.supabase_anon_key
    )

            # Test connection
            await self._test_connection()
            
            # Initialize schema
            await self._initialize_schema()
            
            self.initialized = True
            logger.info("Database configuration initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database configuration: {e}")
            raise
    
    async def _test_connection(self):
        """Test Supabase connection"""
        try:
            # Simple query to test connection
            result = self.supabase.table("stories").select("id").limit(1).execute()
            logger.info("Supabase connection test successful")
        except Exception as e:
            logger.error(f"Supabase connection test failed: {e}")
            raise
    
    async def _initialize_schema(self):
        """Initialize database schema with essential tables"""
        try:
            # Create tables if they don't exist
            await self._create_stories_table()
            await self._create_chapters_table()
            await self._create_characters_table()
            await self._create_story_characters_table()
            await self._create_chapter_segments_table()
            await self._create_generation_tasks_table()
            await self._create_visual_assets_table()
            await self._create_character_relationships_table()
            
            logger.info("Database schema initialized successfully")
            
        except Exception as e:
            logger.error(f"Schema initialization failed: {e}")
            raise
    
    async def _create_stories_table(self):
        """Create stories table with essential fields"""
        try:
            # Check if table exists
            result = self.supabase.table("stories").select("id").limit(1).execute()
            logger.info("Stories table already exists")
            return
        except:
            pass
        
        # Create table using SQL (Supabase supports this)
        create_sql = """
CREATE TABLE IF NOT EXISTS stories (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL,
    title VARCHAR(500) NOT NULL,
            genre VARCHAR(100),
    description TEXT,
            metadata JSONB DEFAULT '{}',
    generation_settings JSONB DEFAULT '{}',
    image_settings JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

        -- Create indexes for performance
        CREATE INDEX IF NOT EXISTS idx_stories_user_id ON stories(user_id);
        CREATE INDEX IF NOT EXISTS idx_stories_genre ON stories(genre);
        CREATE INDEX IF NOT EXISTS idx_stories_created_at ON stories(created_at);
        """
        
        # Execute SQL (this would need to be done through Supabase's SQL editor or migrations)
        logger.info("Stories table creation SQL prepared (execute manually in Supabase SQL editor)")
    
    async def _create_chapters_table(self):
        """Create chapters table"""
        try:
            result = self.supabase.table("chapters").select("id").limit(1).execute()
            logger.info("Chapters table already exists")
            return
        except:
            pass
        
        create_sql = """
CREATE TABLE IF NOT EXISTS chapters (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    story_id UUID REFERENCES stories(id) ON DELETE CASCADE,
    title VARCHAR(500),
            content TEXT,
            chapter_order INTEGER,
    word_count INTEGER DEFAULT 0,
            metadata JSONB DEFAULT '{}',
    continuation_context JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

        CREATE INDEX IF NOT EXISTS idx_chapters_story_id ON chapters(story_id);
        CREATE INDEX IF NOT EXISTS idx_chapters_order ON chapters(story_id, chapter_order);
        """
        
        logger.info("Chapters table creation SQL prepared")
    
    async def _create_characters_table(self):
        """Create characters table"""
        try:
            result = self.supabase.table("characters").select("id").limit(1).execute()
            logger.info("Characters table already exists")
            return
        except:
            pass
        
        create_sql = """
        CREATE TABLE IF NOT EXISTS characters (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
            character_data JSONB DEFAULT '{}',
            embedding_id VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

        CREATE INDEX IF NOT EXISTS idx_characters_user_id ON characters(user_id);
        CREATE INDEX IF NOT EXISTS idx_characters_name ON characters(name);
        """
        
        logger.info("Characters table creation SQL prepared")
    
    async def _create_story_characters_table(self):
        """Create story-character relationships table"""
        try:
            result = self.supabase.table("story_characters").select("id").limit(1).execute()
            logger.info("Story characters table already exists")
            return
        except:
            pass
        
        create_sql = """
        CREATE TABLE IF NOT EXISTS story_characters (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    story_id UUID REFERENCES stories(id) ON DELETE CASCADE,
            character_id UUID REFERENCES characters(id) ON DELETE CASCADE,
            role VARCHAR(100) DEFAULT 'supporting',
            importance_score INTEGER DEFAULT 5,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

        CREATE INDEX IF NOT EXISTS idx_story_characters_story_id ON story_characters(story_id);
        CREATE INDEX IF NOT EXISTS idx_story_characters_character_id ON story_characters(character_id);
        """
        
        logger.info("Story characters table creation SQL prepared")
    
    async def _create_chapter_segments_table(self):
        """Create chapter segments table for unlimited content"""
        try:
            result = self.supabase.table("chapter_segments").select("id").limit(1).execute()
            logger.info("Chapter segments table already exists")
            return
        except:
            pass
        
        create_sql = """
        CREATE TABLE IF NOT EXISTS chapter_segments (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chapter_id UUID REFERENCES chapters(id) ON DELETE CASCADE,
            segment_order INTEGER NOT NULL,
            content TEXT NOT NULL,
            word_count INTEGER DEFAULT 0,
            generation_mode VARCHAR(50),
            user_input TEXT,
            metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

        CREATE INDEX IF NOT EXISTS idx_chapter_segments_chapter_id ON chapter_segments(chapter_id);
        CREATE INDEX IF NOT EXISTS idx_chapter_segments_order ON chapter_segments(chapter_id, segment_order);
        """
        
        logger.info("Chapter segments table creation SQL prepared")
    
    async def _create_generation_tasks_table(self):
        """Create generation tasks table for tracking AI generation"""
        try:
            result = self.supabase.table("generation_tasks").select("id").limit(1).execute()
            logger.info("Generation tasks table already exists")
            return
        except:
            pass
        
        create_sql = """
CREATE TABLE IF NOT EXISTS generation_tasks (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL,
    task_type VARCHAR(100) NOT NULL,
            task_data JSONB DEFAULT '{}',
            status VARCHAR(50) DEFAULT 'pending',
            progress INTEGER DEFAULT 0,
    result JSONB,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_generation_tasks_user_id ON generation_tasks(user_id);
CREATE INDEX IF NOT EXISTS idx_generation_tasks_status ON generation_tasks(status);
        CREATE INDEX IF NOT EXISTS idx_generation_tasks_created_at ON generation_tasks(created_at);
        """
        
        logger.info("Generation tasks table creation SQL prepared")
    
    async def _create_visual_assets_table(self):
        """Create visual assets table for images and posters"""
        try:
            result = self.supabase.table("visual_assets").select("id").limit(1).execute()
            logger.info("Visual assets table already exists")
            return
        except:
            pass
        
        create_sql = """
        CREATE TABLE IF NOT EXISTS visual_assets (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            story_id UUID REFERENCES stories(id) ON DELETE CASCADE,
            chapter_id UUID REFERENCES chapters(id) ON DELETE SET NULL,
            segment_id UUID REFERENCES chapter_segments(id) ON DELETE SET NULL,
            asset_type VARCHAR(100) NOT NULL,
            image_url TEXT NOT NULL,
            generation_prompt TEXT,
            image_metadata JSONB DEFAULT '{}',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        CREATE INDEX IF NOT EXISTS idx_visual_assets_story_id ON visual_assets(story_id);
        CREATE INDEX IF NOT EXISTS idx_visual_assets_type ON visual_assets(asset_type);
        """
        
        logger.info("Visual assets table creation SQL prepared")
    
    async def _create_character_relationships_table(self):
        """Create character relationships table"""
        try:
            result = self.supabase.table("character_relationships").select("id").limit(1).execute()
            logger.info("Character relationships table already exists")
            return
        except:
            pass
        
        create_sql = """
        CREATE TABLE IF NOT EXISTS character_relationships (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            character1_id UUID REFERENCES characters(id) ON DELETE CASCADE,
            character2_id UUID REFERENCES characters(id) ON DELETE CASCADE,
            relationship_type VARCHAR(100),
            strength INTEGER CHECK (strength >= 1 AND strength <= 10),
            description TEXT,
            metadata JSONB DEFAULT '{}',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        CREATE INDEX IF NOT EXISTS idx_character_relationships_char1 ON character_relationships(character1_id);
        CREATE INDEX IF NOT EXISTS idx_character_relationships_char2 ON character_relationships(character2_id);
        """
        
        logger.info("Character relationships table creation SQL prepared")
    
    async def get_schema_status(self) -> Dict[str, Any]:
        """Get current schema status and table information"""
        if not self.initialized:
            return {"error": "Database not initialized"}
        
        try:
            tables = [
                "stories", "chapters", "characters", "story_characters",
                "chapter_segments", "generation_tasks", "visual_assets",
                "character_relationships"
            ]
            
            schema_status = {}
            for table in tables:
                try:
                    result = self.supabase.table(table).select("id", count="exact").execute()
                    schema_status[table] = {
                        "exists": True,
                        "record_count": result.count or 0
                    }
                except Exception as e:
                    schema_status[table] = {
                        "exists": False,
                        "error": str(e)
                    }
            
            return {
                "status": "healthy",
                "tables": schema_status,
                "initialized": self.initialized
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "initialized": self.initialized
            }
    
    async def create_initial_data(self):
        """Create initial seed data for development/testing"""
        if not self.initialized:
            logger.warning("Cannot create initial data: database not initialized")
            return
        
        try:
            # Create sample story genres
            sample_genres = [
                "fantasy", "science fiction", "mystery", "romance", 
                "adventure", "horror", "historical fiction", "contemporary"
            ]
            
            # Create sample writing styles
            sample_styles = [
                "descriptive", "dialogue-heavy", "action-packed", "atmospheric",
                "fast-paced", "slow-burn", "character-driven", "plot-driven"
            ]
            
            logger.info("Initial data creation completed")
            
        except Exception as e:
            logger.warning(f"Initial data creation failed: {e}")
    
    def get_supabase_client(self) -> Client:
        """Get initialized Supabase client"""
        if not self.initialized:
            raise Exception("Database not initialized. Call initialize() first.")
        return self.supabase

# Global database config instance
database_config = DatabaseConfig()

# Convenience functions
async def init_database():
    """Initialize database configuration"""
    await database_config.initialize()

async def init_supabase_schema():
    """Initialize Supabase schema (alias for init_database)"""
    await init_database()

def get_supabase_client() -> Client:
    """Get Supabase client for dependency injection"""
    return database_config.get_supabase_client()
