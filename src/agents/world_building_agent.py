# agents/world_building.py
from typing import Dict, Any, List, Optional
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
import json
import logging

from .base_agent import BaseAgent
from models.generation_models import (
    AgentContext, AgentType, WorldElementType
)
from services.vector_service import VectorService

logger = logging.getLogger(__name__)

class WorldBuildingAgent(BaseAgent):
    """
    World Building Agent
    
    Responsibilities:
    - Setting details and world consistency management
    - Cultural, technological, and magical system development
    - Geographic and environmental descriptions
    - Historical context and timeline management
    - Social and political structure development
    - Economic system design
    - World rule establishment and enforcement
    - Consistency checking across world elements
    """
    
    def __init__(self, vector_service: VectorService):
        super().__init__(
            agent_type=AgentType.WORLD_BUILDING,
            vector_service=vector_service
        )
        self.world_consistency_rules: Dict[str, Dict[str, Any]] = {}
        self.world_element_relationships: Dict[str, List[str]] = {}
    
    def _get_agent_role_description(self) -> str:
        return """
        As the World Building Agent, you are responsible for creating rich, consistent,
        and immersive story worlds that support the narrative and enhance reader engagement.
        
        Your key responsibilities:
        1. Develop detailed setting descriptions that match genre and story needs
        2. Create consistent world rules (magic systems, technology levels, etc.)
        3. Design cultures, societies, and political systems
        4. Establish geographic and environmental details
        5. Maintain historical continuity and timeline consistency
        6. Ensure all world elements work together logically
        7. Adapt world details to support plot and character development
        8. Verify consistency across all story content
        """
    
    async def _execute_task(self, context: AgentContext) -> Dict[str, Any]:
        """
        Execute World Building specific tasks
        """
        task_data = context.agent_specific_data
        task_type = task_data.get("task_type", "enhance_setting")
        
        if task_type == "enhance_setting":
            return await self._enhance_story_setting(context)
        elif task_type == "create_world_element":
            return await self._create_world_element(context)
        elif task_type == "check_world_consistency":
            return await self._check_world_consistency(context)
        elif task_type == "expand_culture":
            return await self._expand_cultural_details(context)
        elif task_type == "develop_history":
            return await self._develop_historical_context(context)
        elif task_type == "design_location":
            return await self._design_specific_location(context)
        else:
            raise ValueError(f"Unknown task type: {task_type}")
    
    async def _enhance_story_setting(self, context: AgentContext) -> Dict[str, Any]:
        """
        Enhance the story setting based on content and requirements
        """
        logger.info(f"Enhancing story setting for task {context.task_id}")
        
        # 1. Analyze current content for setting needs
        setting_analysis = await self._analyze_setting_requirements(context)
        
        # 2. Gather existing world context
        world_context = await self._gather_world_context(context)
        
        # 3. Identify enhancement opportunities
        enhancement_opportunities = await self._identify_enhancement_opportunities(
            context, setting_analysis, world_context
        )
        
        # 4. Generate setting enhancements
        setting_enhancements = await self._generate_setting_enhancements(
            context, enhancement_opportunities, world_context
        )
        
        # 5. Ensure consistency with existing world
        consistency_check = await self._validate_world_consistency(
            context, setting_enhancements, world_context
        )
        
        # 6. Store new world elements
        await self._store_world_elements(context, setting_enhancements)
        
        return {
            "setting_enhancements": setting_enhancements,
            "world_elements_added": setting_enhancements.get("elements_added", []),
            "consistency_validation": consistency_check,
            "enhancement_opportunities": enhancement_opportunities,
            "integration_notes": setting_enhancements.get("integration_notes", []),
            "future_development_suggestions": setting_enhancements.get("future_suggestions", [])
        }
    
    async def _analyze_setting_requirements(self, context: AgentContext) -> Dict[str, Any]:
        """
        Analyze the current content to determine setting enhancement needs
        """
        content = context.agent_specific_data.get("content", "")
        user_input = context.user_input or ""
        story_metadata = context.story_context.story_metadata
        
        analysis_prompt = """
        Analyze the content and determine what setting/world-building enhancements are needed:
        
        Story Content: {content}
        User Input: {user_input}
        
        Story Context:
        - Genre: {genre}
        - Setting Time Period: {time_period}
        - Setting Location: {location}
        - Target Audience: {target_audience}
        
        Identify setting requirements in JSON format:
        {{
            "setting_elements_mentioned": ["locations, cultures, systems mentioned"],
            "setting_gaps": ["missing world details that would enhance the story"],
            "enhancement_priorities": [
                {{
                    "element_type": "location|culture|technology|magic|politics|economy|history",
                    "priority": "high|medium|low",
                    "reason": "why this enhancement is needed",
                    "specific_requirements": "what specifically needs to be developed"
                }}
            ],
            "consistency_requirements": ["existing elements that must be maintained"],
            "genre_expectations": ["world-building elements expected for this genre"],
            "atmosphere_needs": ["mood and atmosphere requirements"],
            "plot_support_needs": ["world elements needed to support plot"]
        }}
        """
        
        context_vars = {
            "content": content[:1500],
            "user_input": user_input,
            "genre": story_metadata.get("genre", "Unknown"),
            "time_period": story_metadata.get("setting_time_period", "Unspecified"),
            "location": story_metadata.get("setting_location", "Unspecified"),
            "target_audience": story_metadata.get("target_audience", "adult")
        }
        
        result = await self._generate_with_llm(
            analysis_prompt,
            context_vars,
            JsonOutputParser()
        )
        
        return result
    
    async def _gather_world_context(self, context: AgentContext) -> Dict[str, Any]:
        """
        Gather existing world-building context from vector database
        """
        story_context = context.story_context
        search_query = f"world building {story_context.story_metadata.get('genre', '')}"
        
        world_context = {}
        
        # Get world-building context
        world_elements = await self._get_relevant_context(
            story_context, search_query, "world", max_results=10
        )
        world_context["existing_elements"] = world_elements
        
        # Get setting context from general story context
        general_context = await self._get_relevant_context(
            story_context, "setting location description", "general", max_results=5
        )
        world_context["setting_descriptions"] = general_context
        
        # Extract world elements from story metadata
        world_context["story_metadata"] = {
            "genre": story_context.story_metadata.get("genre"),
            "time_period": story_context.story_metadata.get("setting_time_period"),
            "location": story_context.story_metadata.get("setting_location"),
            "themes": story_context.story_metadata.get("themes", [])
        }
        
        return world_context
    
    async def _identify_enhancement_opportunities(
        self,
        context: AgentContext,
        setting_analysis: Dict[str, Any],
        world_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Identify specific opportunities for world-building enhancement
        """
        enhancement_prompt = """
        Based on the setting analysis and existing world context, identify enhancement opportunities:
        
        Setting Analysis: {setting_analysis}
        Existing World Elements: {existing_elements}
        Story Metadata: {story_metadata}
        
        Identify enhancement opportunities in JSON format:
        {{
            "immediate_opportunities": [
                {{
                    "element_type": "location|culture|technology|magic|politics|economy|history",
                    "description": "what to enhance or create",
                    "impact": "how this will improve the story",
                    "complexity": "simple|moderate|complex",
                    "dependencies": ["other elements this depends on"]
                }}
            ],
            "long_term_development": ["opportunities for future development"],
            "consistency_improvements": ["ways to improve world consistency"],
            "atmosphere_enhancements": ["ways to improve mood and atmosphere"],
            "genre_alignment": ["enhancements to better fit genre expectations"]
        }}
        """
        
        context_vars = {
            "setting_analysis": json.dumps(setting_analysis, indent=2),
            "existing_elements": json.dumps(world_context.get("existing_elements", [])[:5]),
            "story_metadata": json.dumps(world_context.get("story_metadata", {}))
        }
        
        result = await self._generate_with_llm(
            enhancement_prompt,
            context_vars,
            JsonOutputParser()
        )
        
        return result
    
    async def _generate_setting_enhancements(
        self,
        context: AgentContext,
        enhancement_opportunities: Dict[str, Any],
        world_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate specific setting enhancements
        """
        immediate_opportunities = enhancement_opportunities.get("immediate_opportunities", [])
        
        enhancements = {
            "elements_added": [],
            "descriptions_enhanced": [],
            "consistency_rules": [],
            "integration_notes": [],
            "future_suggestions": []
        }
        
        # Process immediate opportunities
        for opportunity in immediate_opportunities[:3]:  # Limit to top 3
            element_type = opportunity.get("element_type", "location")
            enhancement = await self._generate_specific_enhancement(
                context, opportunity, world_context
            )
            
            if enhancement:
                enhancements["elements_added"].append({
                    "type": element_type,
                    "content": enhancement,
                    "integration_notes": opportunity.get("description", "")
                })
        
        # Add long-term suggestions
        enhancements["future_suggestions"] = enhancement_opportunities.get("long_term_development", [])
        
        return enhancements
    
    async def _generate_specific_enhancement(
        self,
        context: AgentContext,
        opportunity: Dict[str, Any],
        world_context: Dict[str, Any]
    ) -> Optional[str]:
        """
        Generate a specific world-building enhancement
        """
        element_type = opportunity.get("element_type", "location")
        description = opportunity.get("description", "")
        
        # Create element-specific prompts
        if element_type == "location":
            return await self._generate_location_description(context, opportunity, world_context)
        elif element_type == "culture":
            return await self._generate_cultural_details(context, opportunity, world_context)
        elif element_type == "technology":
            return await self._generate_technology_details(context, opportunity, world_context)
        elif element_type == "magic":
            return await self._generate_magic_system_details(context, opportunity, world_context)
        elif element_type == "politics":
            return await self._generate_political_details(context, opportunity, world_context)
        elif element_type == "history":
            return await self._generate_historical_details(context, opportunity, world_context)
        else:
            return await self._generate_general_world_element(context, opportunity, world_context)
    
    async def _generate_location_description(
        self,
        context: AgentContext,
        opportunity: Dict[str, Any],
        world_context: Dict[str, Any]
    ) -> str:
        """
        Generate detailed location description
        """
        location_prompt = """
        Create a rich, immersive location description based on the requirements:
        
        Requirements: {requirements}
        Existing World Context: {world_context}
        Genre: {genre}
        
        Create a detailed location description that:
        1. Fits the genre and story tone
        2. Supports the narrative needs
        3. Is consistent with existing world elements
        4. Engages the senses and creates atmosphere
        5. Includes practical details characters might interact with
        
        Write a compelling location description (150-250 words) that brings the place to life.
        """
        
        context_vars = {
            "requirements": opportunity.get("description", ""),
            "world_context": json.dumps(world_context.get("story_metadata", {})),
            "genre": context.story_context.story_metadata.get("genre", "general")
        }
        
        result = await self._generate_with_llm(
            location_prompt,
            context_vars,
            StrOutputParser()
        )
        
        return result
    
    async def _generate_cultural_details(
        self,
        context: AgentContext,
        opportunity: Dict[str, Any],
        world_context: Dict[str, Any]
    ) -> str:
        """
        Generate cultural details and customs
        """
        culture_prompt = """
        Develop cultural details that enhance the story world:
        
        Cultural Requirements: {requirements}
        Existing World: {world_context}
        Genre: {genre}
        Target Audience: {target_audience}
        
        Create cultural details including:
        1. Social customs and traditions
        2. Values and beliefs
        3. Communication styles
        4. Social hierarchy or structure
        5. Unique cultural elements that fit the genre
        
        Write engaging cultural details (150-200 words) that feel authentic and support the story.
        """
        
        context_vars = {
            "requirements": opportunity.get("description", ""),
            "world_context": json.dumps(world_context.get("story_metadata", {})),
            "genre": context.story_context.story_metadata.get("genre", "general"),
            "target_audience": context.story_context.story_metadata.get("target_audience", "adult")
        }
        
        result = await self._generate_with_llm(
            culture_prompt,
            context_vars,
            StrOutputParser()
        )
        
        return result
    
    async def _generate_technology_details(
        self,
        context: AgentContext,
        opportunity: Dict[str, Any],
        world_context: Dict[str, Any]
    ) -> str:
        """
        Generate technology system details
        """
        tech_prompt = """
        Develop technology details that fit the story world:
        
        Technology Requirements: {requirements}
        World Context: {world_context}
        Genre: {genre}
        Time Period: {time_period}
        
        Create technology details including:
        1. Level of technological advancement
        2. Key technologies that impact daily life
        3. How technology affects society and characters
        4. Limitations and capabilities
        5. How technology integrates with other world elements
        
        Write coherent technology details (150-200 words) that enhance the story world.
        """
        
        context_vars = {
            "requirements": opportunity.get("description", ""),
            "world_context": json.dumps(world_context.get("story_metadata", {})),
            "genre": context.story_context.story_metadata.get("genre", "general"),
            "time_period": context.story_context.story_metadata.get("setting_time_period", "unspecified")
        }
        
        result = await self._generate_with_llm(
            tech_prompt,
            context_vars,
            StrOutputParser()
        )
        
        return result
    
    async def _generate_magic_system_details(
        self,
        context: AgentContext,
        opportunity: Dict[str, Any],
        world_context: Dict[str, Any]
    ) -> str:
        """
        Generate magic system details for fantasy genres
        """
        magic_prompt = """
        Develop magic system details for this fantasy world:
        
        Magic Requirements: {requirements}
        World Context: {world_context}
        Genre: {genre}
        
        Create magic system details including:
        1. How magic works (rules and limitations)
        2. Who can use magic and how it's learned
        3. Cost or consequences of using magic
        4. How magic affects society and daily life
        5. Different types or schools of magic
        
        Write a coherent magic system (150-250 words) with clear rules and interesting limitations.
        """
        
        context_vars = {
            "requirements": opportunity.get("description", ""),
            "world_context": json.dumps(world_context.get("story_metadata", {})),
            "genre": context.story_context.story_metadata.get("genre", "fantasy")
        }
        
        result = await self._generate_with_llm(
            magic_prompt,
            context_vars,
            StrOutputParser()
        )
        
        return result
    
    async def _generate_political_details(
        self,
        context: AgentContext,
        opportunity: Dict[str, Any],
        world_context: Dict[str, Any]
    ) -> str:
        """
        Generate political system details
        """
        politics_prompt = """
        Develop political system details for the story world:
        
        Political Requirements: {requirements}
        World Context: {world_context}
        Genre: {genre}
        
        Create political details including:
        1. Government structure and leadership
        2. Power dynamics and conflicts
        3. Laws and social order
        4. How politics affects characters and plot
        5. Current political tensions or issues
        
        Write political details (150-200 words) that create interesting story opportunities.
        """
        
        context_vars = {
            "requirements": opportunity.get("description", ""),
            "world_context": json.dumps(world_context.get("story_metadata", {})),
            "genre": context.story_context.story_metadata.get("genre", "general")
        }
        
        result = await self._generate_with_llm(
            politics_prompt,
            context_vars,
            StrOutputParser()
        )
        
        return result
    
    async def _generate_historical_details(
        self,
        context: AgentContext,
        opportunity: Dict[str, Any],
        world_context: Dict[str, Any]
    ) -> str:
        """
        Generate historical context and background
        """
        history_prompt = """
        Develop historical details that enrich the story world:
        
        Historical Requirements: {requirements}
        World Context: {world_context}
        Genre: {genre}
        
        Create historical details including:
        1. Important past events that shaped the current world
        2. Historical figures or legends
        3. How history affects current situations
        4. Cultural memory and traditions
        5. Historical conflicts or achievements
        
        Write historical background (150-200 words) that adds depth to the current story.
        """
        
        context_vars = {
            "requirements": opportunity.get("description", ""),
            "world_context": json.dumps(world_context.get("story_metadata", {})),
            "genre": context.story_context.story_metadata.get("genre", "general")
        }
        
        result = await self._generate_with_llm(
            history_prompt,
            context_vars,
            StrOutputParser()
        )
        
        return result
    
    async def _generate_general_world_element(
        self,
        context: AgentContext,
        opportunity: Dict[str, Any],
        world_context: Dict[str, Any]
    ) -> str:
        """
        Generate general world-building element
        """
        general_prompt = """
        Develop world-building details for the story:
        
        Requirements: {requirements}
        Element Type: {element_type}
        World Context: {world_context}
        Genre: {genre}
        
        Create detailed world-building content that:
        1. Fits the specified element type
        2. Enhances the story atmosphere
        3. Is consistent with existing world elements
        4. Supports character and plot development
        5. Creates interesting story opportunities
        
        Write compelling world-building details (150-250 words).
        """
        
        context_vars = {
            "requirements": opportunity.get("description", ""),
            "element_type": opportunity.get("element_type", "general"),
            "world_context": json.dumps(world_context.get("story_metadata", {})),
            "genre": context.story_context.story_metadata.get("genre", "general")
        }
        
        result = await self._generate_with_llm(
            general_prompt,
            context_vars,
            StrOutputParser()
        )
        
        return result
    
    async def _validate_world_consistency(
        self,
        context: AgentContext,
        setting_enhancements: Dict[str, Any],
        world_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate that new world elements are consistent with existing world
        """
        consistency_prompt = """
        Check the consistency of new world elements with existing world context:
        
        New Elements: {new_elements}
        Existing World: {existing_world}
        Genre: {genre}
        
        Evaluate consistency in JSON format:
        {{
            "consistency_score": 0.0-1.0,
            "consistent_elements": ["elements that fit well with existing world"],
            "potential_conflicts": ["elements that might conflict with existing world"],
            "integration_suggestions": ["how to better integrate new elements"],
            "world_rule_violations": ["any violations of established world rules"],
            "enhancement_opportunities": ["ways the new elements enhance the world"]
        }}
        """
        
        context_vars = {
            "new_elements": json.dumps(setting_enhancements.get("elements_added", [])),
            "existing_world": json.dumps(world_context.get("existing_elements", [])[:5]),
            "genre": context.story_context.story_metadata.get("genre", "general")
        }
        
        result = await self._generate_with_llm(
            consistency_prompt,
            context_vars,
            JsonOutputParser()
        )
        
        return result
    
    async def _store_world_elements(
        self,
        context: AgentContext,
        setting_enhancements: Dict[str, Any]
    ):
        """
        Store new world elements in vector database
        """
        try:
            elements_added = setting_enhancements.get("elements_added", [])
            
            for element in elements_added:
                element_content = element.get("content", "")
                element_type = element.get("type", "general")
                
                await self._store_result_in_vector_db(
                    content=element_content,
                    metadata={
                        "story_id": str(context.story_context.story_id),
                        "element_type": element_type,
                        "agent_type": "world_building",
                        "integration_notes": element.get("integration_notes", ""),
                        "timestamp": context.task_id
                    },
                    collection_name="world_embeddings"
                )
                
        except Exception as e:
            logger.warning(f"Failed to store world elements: {e}")
    
    async def _check_world_consistency(self, context: AgentContext) -> Dict[str, Any]:
        """
        Comprehensive world consistency check
        """
        # Get all world elements for this story
        story_context = context.story_context
        
        world_elements = await self._get_relevant_context(
            story_context, "world elements", "world", max_results=20
        )
        
        if not world_elements:
            return {
                "consistency_score": 1.0,
                "issues_found": [],
                "suggestions": ["No world elements found to check consistency"]
            }
        
        consistency_prompt = """
        Perform a comprehensive world consistency check:
        
        World Elements: {world_elements}
        Genre: {genre}
        
        Check for consistency issues in JSON format:
        {{
            "consistency_score": 0.0-1.0,
            "issues_found": [
                {{
                    "issue_type": "contradiction|logic_error|genre_mismatch",
                    "description": "what the issue is",
                    "elements_involved": ["which elements are inconsistent"],
                    "severity": "low|medium|high"
                }}
            ],
            "suggestions": ["how to resolve consistency issues"],
            "strengths": ["aspects of the world that work well together"],
            "improvement_opportunities": ["ways to enhance world consistency"]
        }}
        """
        
        context_vars = {
            "world_elements": json.dumps(world_elements[:10], indent=2),
            "genre": story_context.story_metadata.get("genre", "general")
        }
        
        result = await self._generate_with_llm(
            consistency_prompt,
            context_vars,
            JsonOutputParser()
        )
        
        return result
