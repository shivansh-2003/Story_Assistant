# agents/quality_assurance.py
from typing import Dict, Any, List, Optional, Tuple
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
import json
import re
import logging
from textstat import flesch_reading_ease, flesch_kincaid_grade
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from collections import Counter

from .base_agent import BaseAgent
from models.generation_models import (
    AgentContext, AgentType, QualityMetrics
)
from services.vector_service import VectorService

logger = logging.getLogger(__name__)

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

class QualityAssuranceAgent(BaseAgent):
    """
    Quality Assurance Agent
    
    Responsibilities:
    - Grammar and style checking
    - Character consistency validation (embedding similarity)
    - Plot hole detection (logical inference chains)
    - Genre adherence verification
    - Readability analysis
    - Content appropriateness for target audience
    - Automated error correction suggestions
    - Quality scoring and improvement recommendations
    """
    
    def __init__(self, vector_service: VectorService):
        super().__init__(
            agent_type=AgentType.QUALITY_ASSURANCE,
            vector_service=vector_service
        )
        self.quality_history: List[Dict[str, Any]] = []
        self.character_consistency_cache: Dict[str, Dict[str, Any]] = {}
    
    def _get_agent_role_description(self) -> str:
        return """
        As the Quality Assurance Agent, you are responsible for ensuring all generated 
        content meets high standards of quality, consistency, and appropriateness.
        
        Your key responsibilities:
        1. Analyze grammar, spelling, and writing mechanics
        2. Verify character consistency across all content
        3. Check plot coherence and identify potential plot holes
        4. Ensure genre conventions are followed appropriately
        5. Evaluate readability for target audience
        6. Assess content appropriateness and safety
        7. Provide specific improvement suggestions
        8. Generate quality scores and metrics
        9. Recommend corrections and enhancements
        """
    
    async def _execute_task(self, context: AgentContext) -> Dict[str, Any]:
        """
        Execute Quality Assurance specific tasks
        """
        task_data = context.agent_specific_data
        task_type = task_data.get("task_type", "full_quality_check")
        
        if task_type == "full_quality_check":
            return await self._perform_full_quality_check(context)
        elif task_type == "grammar_check":
            return await self._check_grammar_and_style(context)
        elif task_type == "character_consistency_check":
            return await self._check_character_consistency(context)
        elif task_type == "plot_coherence_check":
            return await self._check_plot_coherence(context)
        elif task_type == "genre_adherence_check":
            return await self._check_genre_adherence(context)
        elif task_type == "readability_analysis":
            return await self._analyze_readability(context)
        else:
            raise ValueError(f"Unknown task type: {task_type}")
    
    async def _perform_full_quality_check(self, context: AgentContext) -> Dict[str, Any]:
        """
        Perform comprehensive quality assessment
        """
        logger.info(f"Performing full quality check for task {context.task_id}")
        
        content = context.agent_specific_data.get("content", "")
        if not content:
            raise ValueError("No content provided for quality check")
        
        # Perform all quality checks
        grammar_results = await self._check_grammar_and_style(context)
        character_results = await self._check_character_consistency(context)
        plot_results = await self._check_plot_coherence(context)
        genre_results = await self._check_genre_adherence(context)
        readability_results = await self._analyze_readability(context)
        
        # Calculate overall quality metrics
        quality_metrics = self._calculate_overall_quality_metrics(
            grammar_results, character_results, plot_results, 
            genre_results, readability_results
        )
        
        # Generate improvement suggestions
        improvement_suggestions = await self._generate_improvement_suggestions(
            context, grammar_results, character_results, plot_results, 
            genre_results, readability_results
        )
        
        # Determine if human review is needed
        requires_human_review = self._assess_human_review_requirement(quality_metrics)
        
        # Store quality assessment for learning
        await self._store_quality_assessment(context, quality_metrics, improvement_suggestions)
        
        return {
            "quality_metrics": quality_metrics.dict(),
            "grammar_analysis": grammar_results,
            "character_consistency": character_results,
            "plot_coherence": plot_results,
            "genre_adherence": genre_results,
            "readability_analysis": readability_results,
            "improvement_suggestions": improvement_suggestions,
            "requires_human_review": requires_human_review,
            "overall_assessment": self._generate_overall_assessment(quality_metrics),
            "auto_corrections": await self._generate_auto_corrections(context, grammar_results)
        }
    
    async def _check_grammar_and_style(self, context: AgentContext) -> Dict[str, Any]:
        """
        Check grammar, spelling, and writing style
        """
        content = context.agent_specific_data.get("content", "")
        target_audience = context.story_context.story_metadata.get("target_audience", "adult")
        writing_style = context.story_context.story_metadata.get("writing_style", "balanced")
        
        grammar_prompt = """
        Analyze the following text for grammar, spelling, and style issues:
        
        Content: {content}
        
        Target Audience: {target_audience}
        Writing Style: {writing_style}
        
        Provide a detailed analysis in JSON format:
        {{
            "grammar_issues": [
                {{
                    "issue": "description of the issue",
                    "location": "approximate location in text",
                    "severity": "low|medium|high",
                    "suggestion": "how to fix it"
                }}
            ],
            "style_observations": [
                {{
                    "aspect": "sentence_length|word_choice|tone|flow",
                    "observation": "what was observed",
                    "suggestion": "improvement suggestion"
                }}
            ],
            "spelling_errors": ["list of potential spelling errors"],
            "punctuation_issues": ["punctuation problems found"],
            "consistency_issues": ["style consistency problems"],
            "grammar_score": 0.0-1.0,
            "style_appropriateness": 0.0-1.0,
            "overall_mechanics_score": 0.0-1.0
        }}
        """
        
        context_vars = {
            "content": content[:2000],  # Limit for prompt size
            "target_audience": target_audience,
            "writing_style": writing_style
        }
        
        result = await self._generate_with_llm(
            grammar_prompt,
            context_vars,
            JsonOutputParser()
        )
        
        # Add basic readability metrics
        result["readability_metrics"] = self._calculate_basic_readability(content)
        
        return result
    
    async def _check_character_consistency(self, context: AgentContext) -> Dict[str, Any]:
        """
        Check character consistency using vector similarity and LLM analysis
        """
        content = context.agent_specific_data.get("content", "")
        characters_in_content = self._extract_characters_from_content(content, context)
        
        if not characters_in_content:
            return {
                "characters_analyzed": [],
                "consistency_scores": {},
                "consistency_issues": [],
                "overall_character_consistency": 1.0
            }
        
        consistency_results = {}
        consistency_issues = []
        
        for character_name in characters_in_content:
            # Get character's established traits from vector database
            character_context = await self._get_character_established_traits(
                character_name, context.story_context
            )
            
            if character_context:
                # Analyze consistency with LLM
                consistency_analysis = await self._analyze_character_consistency_llm(
                    character_name, content, character_context
                )
                
                consistency_results[character_name] = consistency_analysis
                
                if consistency_analysis.get("consistency_score", 1.0) < 0.8:
                    consistency_issues.extend(consistency_analysis.get("issues", []))
        
        # Calculate overall consistency score
        overall_score = 1.0
        if consistency_results:
            scores = [result.get("consistency_score", 1.0) for result in consistency_results.values()]
            overall_score = sum(scores) / len(scores)
        
        return {
            "characters_analyzed": list(characters_in_content),
            "consistency_scores": {k: v.get("consistency_score", 1.0) for k, v in consistency_results.items()},
            "consistency_issues": consistency_issues,
            "detailed_analysis": consistency_results,
            "overall_character_consistency": overall_score
        }
    
    async def _check_plot_coherence(self, context: AgentContext) -> Dict[str, Any]:
        """
        Check plot coherence and identify potential plot holes
        """
        content = context.agent_specific_data.get("content", "")
        previous_content = context.story_context.previous_content or ""
        
        plot_prompt = """
        Analyze the plot coherence and identify any logical inconsistencies or plot holes:
        
        Previous Content Context: {previous_content}
        Current Content: {current_content}
        
        Genre: {genre}
        Story Metadata: {story_metadata}
        
        Analyze for plot coherence in JSON format:
        {{
            "plot_holes": [
                {{
                    "issue": "description of the plot hole",
                    "severity": "minor|moderate|major",
                    "suggestion": "how to address it"
                }}
            ],
            "logical_inconsistencies": [
                {{
                    "inconsistency": "what doesn't make sense",
                    "context": "where it occurs",
                    "impact": "how it affects the story"
                }}
            ],
            "timeline_issues": ["chronological problems"],
            "character_motivation_issues": ["character actions that don't make sense"],
            "world_consistency_issues": ["contradictions with established world rules"],
            "plot_coherence_score": 0.0-1.0,
            "narrative_flow_score": 0.0-1.0,
            "overall_logic_score": 0.0-1.0
        }}
        """
        
        context_vars = {
            "previous_content": previous_content[-1000:] if previous_content else "No previous content",
            "current_content": content[:1500],
            "genre": context.story_context.story_metadata.get("genre", "Unknown"),
            "story_metadata": json.dumps(context.story_context.story_metadata)
        }
        
        result = await self._generate_with_llm(
            plot_prompt,
            context_vars,
            JsonOutputParser()
        )
        
        return result
    
    async def _check_genre_adherence(self, context: AgentContext) -> Dict[str, Any]:
        """
        Check adherence to genre conventions and expectations
        """
        content = context.agent_specific_data.get("content", "")
        genre = context.story_context.story_metadata.get("genre", "general")
        target_audience = context.story_context.story_metadata.get("target_audience", "adult")
        
        genre_prompt = """
        Analyze how well this content adheres to {genre} genre conventions:
        
        Content: {content}
        Target Audience: {target_audience}
        
        Evaluate genre adherence in JSON format:
        {{
            "genre_conventions_followed": ["conventions that are properly followed"],
            "genre_conventions_missed": ["expected conventions that are missing"],
            "inappropriate_elements": ["elements that don't fit the genre"],
            "tone_appropriateness": 0.0-1.0,
            "content_appropriateness": 0.0-1.0,
            "audience_appropriateness": 0.0-1.0,
            "genre_authenticity_score": 0.0-1.0,
            "suggestions_for_improvement": ["how to better fit genre expectations"]
        }}
        """
        
        context_vars = {
            "content": content[:1500],
            "genre": genre,
            "target_audience": target_audience
        }
        
        result = await self._generate_with_llm(
            genre_prompt,
            context_vars,
            JsonOutputParser()
        )
        
        return result
    
    async def _analyze_readability(self, context: AgentContext) -> Dict[str, Any]:
        """
        Analyze readability and complexity for target audience
        """
        content = context.agent_specific_data.get("content", "")
        target_audience = context.story_context.story_metadata.get("target_audience", "adult")
        
        # Calculate readability metrics
        readability_metrics = self._calculate_detailed_readability(content)
        
        # Analyze appropriateness for target audience
        readability_prompt = """
        Analyze the readability and complexity of this content for {target_audience} audience:
        
        Content: {content}
        
        Readability Metrics:
        - Flesch Reading Ease: {flesch_ease}
        - Flesch-Kincaid Grade: {fk_grade}
        - Average Sentence Length: {avg_sentence_length}
        - Average Word Length: {avg_word_length}
        
        Provide readability analysis in JSON format:
        {{
            "age_appropriateness": 0.0-1.0,
            "vocabulary_appropriateness": 0.0-1.0,
            "sentence_complexity_appropriateness": 0.0-1.0,
            "overall_readability_score": 0.0-1.0,
            "reading_level_assessment": "too_easy|appropriate|too_difficult",
            "vocabulary_concerns": ["difficult words for target audience"],
            "sentence_structure_concerns": ["overly complex sentences"],
            "improvement_suggestions": ["how to improve readability"]
        }}
        """
        
        context_vars = {
            "content": content[:1500],
            "target_audience": target_audience,
            "flesch_ease": readability_metrics.get("flesch_ease", 0),
            "fk_grade": readability_metrics.get("fk_grade", 0),
            "avg_sentence_length": readability_metrics.get("avg_sentence_length", 0),
            "avg_word_length": readability_metrics.get("avg_word_length", 0)
        }
        
        llm_analysis = await self._generate_with_llm(
            readability_prompt,
            context_vars,
            JsonOutputParser()
        )
        
        # Combine metrics and LLM analysis
        return {
            **readability_metrics,
            **llm_analysis
        }
    
    def _calculate_overall_quality_metrics(
        self,
        grammar_results: Dict[str, Any],
        character_results: Dict[str, Any],
        plot_results: Dict[str, Any],
        genre_results: Dict[str, Any],
        readability_results: Dict[str, Any]
    ) -> QualityMetrics:
        """
        Calculate overall quality metrics from individual assessments
        """
        grammar_score = grammar_results.get("overall_mechanics_score", 0.8)
        readability_score = readability_results.get("overall_readability_score", 0.8)
        character_consistency_score = character_results.get("overall_character_consistency", 0.8)
        plot_coherence_score = plot_results.get("overall_logic_score", 0.8)
        genre_adherence_score = genre_results.get("genre_authenticity_score", 0.8)
        
        # Calculate weighted overall score
        weights = {
            "grammar": 0.25,
            "readability": 0.15,
            "character_consistency": 0.25,
            "plot_coherence": 0.25,
            "genre_adherence": 0.10
        }
        
        overall_score = (
            grammar_score * weights["grammar"] +
            readability_score * weights["readability"] +
            character_consistency_score * weights["character_consistency"] +
            plot_coherence_score * weights["plot_coherence"] +
            genre_adherence_score * weights["genre_adherence"]
        )
        
        return QualityMetrics(
            grammar_score=grammar_score,
            readability_score=readability_score,
            character_consistency_score=character_consistency_score,
            plot_coherence_score=plot_coherence_score,
            genre_adherence_score=genre_adherence_score,
            overall_quality_score=overall_score
        )
    
    async def _generate_improvement_suggestions(
        self,
        context: AgentContext,
        grammar_results: Dict[str, Any],
        character_results: Dict[str, Any],
        plot_results: Dict[str, Any],
        genre_results: Dict[str, Any],
        readability_results: Dict[str, Any]
    ) -> List[str]:
        """
        Generate prioritized improvement suggestions
        """
        suggestions = []
        
        # Grammar suggestions
        if grammar_results.get("overall_mechanics_score", 1.0) < 0.8:
            grammar_issues = grammar_results.get("grammar_issues", [])
            for issue in grammar_issues[:3]:  # Top 3 issues
                if issue.get("severity") in ["medium", "high"]:
                    suggestions.append(f"Grammar: {issue.get('suggestion', '')}")
        
        # Character consistency suggestions
        if character_results.get("overall_character_consistency", 1.0) < 0.8:
            issues = character_results.get("consistency_issues", [])
            suggestions.extend(issues[:2])  # Top 2 character issues
        
        # Plot coherence suggestions
        plot_holes = plot_results.get("plot_holes", [])
        for hole in plot_holes:
            if hole.get("severity") in ["moderate", "major"]:
                suggestions.append(f"Plot: {hole.get('suggestion', '')}")
        
        # Genre adherence suggestions
        genre_suggestions = genre_results.get("suggestions_for_improvement", [])
        suggestions.extend(genre_suggestions[:2])
        
        # Readability suggestions
        readability_suggestions = readability_results.get("improvement_suggestions", [])
        suggestions.extend(readability_suggestions[:2])
        
        return suggestions[:10]  # Limit to top 10 suggestions
    
    def _assess_human_review_requirement(self, quality_metrics: QualityMetrics) -> bool:
        """
        Determine if human review is required based on quality scores
        """
        # Require human review if any major score is below threshold
        critical_thresholds = {
            "overall_quality_score": 0.6,
            "character_consistency_score": 0.7,
            "plot_coherence_score": 0.7,
            "grammar_score": 0.8
        }
        
        for metric, threshold in critical_thresholds.items():
            if getattr(quality_metrics, metric) < threshold:
                return True
        
        return False
    
    def _generate_overall_assessment(self, quality_metrics: QualityMetrics) -> str:
        """
        Generate human-readable overall assessment
        """
        overall_score = quality_metrics.overall_quality_score
        
        if overall_score >= 0.9:
            return "Excellent quality. Content is ready for publication."
        elif overall_score >= 0.8:
            return "High quality. Minor improvements recommended."
        elif overall_score >= 0.7:
            return "Good quality. Some improvements needed before publication."
        elif overall_score >= 0.6:
            return "Acceptable quality. Significant improvements recommended."
        else:
            return "Quality below standards. Major revisions required."
    
    async def _generate_auto_corrections(
        self, 
        context: AgentContext, 
        grammar_results: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Generate automatic corrections for simple grammar and style issues
        """
        content = context.agent_specific_data.get("content", "")
        auto_corrections = {}
        
        # Simple corrections for common issues
        grammar_issues = grammar_results.get("grammar_issues", [])
        
        for issue in grammar_issues:
            if issue.get("severity") == "low":
                # For demo purposes, we'll implement simple corrections
                # In a full implementation, you'd use more sophisticated NLP
                location = issue.get("location", "")
                suggestion = issue.get("suggestion", "")
                
                if "double space" in issue.get("issue", "").lower():
                    auto_corrections["double_spaces"] = "Replace double spaces with single spaces"
                elif "comma splice" in issue.get("issue", "").lower():
                    auto_corrections["comma_splice"] = suggestion
        
        return auto_corrections
    
    def _calculate_basic_readability(self, content: str) -> Dict[str, float]:
        """
        Calculate basic readability metrics
        """
        if not content:
            return {}
        
        try:
            return {
                "flesch_ease": flesch_reading_ease(content),
                "fk_grade": flesch_kincaid_grade(content)
            }
        except Exception as e:
            logger.warning(f"Failed to calculate readability: {e}")
            return {}
    
    def _calculate_detailed_readability(self, content: str) -> Dict[str, Any]:
        """
        Calculate detailed readability and complexity metrics
        """
        if not content:
            return {}
        
        try:
            sentences = sent_tokenize(content)
            words = word_tokenize(content)
            
            # Filter out punctuation for word analysis
            words_only = [word for word in words if word.isalpha()]
            
            metrics = {
                "sentence_count": len(sentences),
                "word_count": len(words_only),
                "avg_sentence_length": len(words_only) / len(sentences) if sentences else 0,
                "avg_word_length": sum(len(word) for word in words_only) / len(words_only) if words_only else 0,
                "flesch_ease": flesch_reading_ease(content),
                "fk_grade": flesch_kincaid_grade(content)
            }
            
            # Calculate vocabulary complexity
            word_freq = Counter(word.lower() for word in words_only)
            unique_words = len(word_freq)
            vocab_diversity = unique_words / len(words_only) if words_only else 0
            
            metrics.update({
                "unique_words": unique_words,
                "vocabulary_diversity": vocab_diversity,
                "repeated_words": len([word for word, freq in word_freq.items() if freq > 3])
            })
            
            return metrics
            
        except Exception as e:
            logger.warning(f"Failed to calculate detailed readability: {e}")
            return {}
    
    def _extract_characters_from_content(
        self, 
        content: str, 
        context: AgentContext
    ) -> List[str]:
        """
        Extract character names mentioned in the content
        """
        characters_mentioned = []
        
        # Get character names from story context
        story_characters = context.story_context.characters
        
        for character in story_characters:
            char_name = character.get("name", "")
            if char_name and char_name.lower() in content.lower():
                characters_mentioned.append(char_name)
        
        return characters_mentioned
    
    async def _get_character_established_traits(
        self, 
        character_name: str, 
        story_context: Any
    ) -> Optional[Dict[str, Any]]:
        """
        Get established character traits from vector database
        """
        try:
            # Search for character information
            character_docs = await self._get_relevant_context(
                story_context, 
                f"character {character_name} personality traits description",
                "character",
                max_results=5
            )
            
            if character_docs:
                # Combine character information
                traits = {}
                for doc in character_docs:
                    metadata = doc.get("metadata", {})
                    traits.update(metadata)
                
                return traits
            
            return None
            
        except Exception as e:
            logger.warning(f"Failed to get character traits for {character_name}: {e}")
            return None
    
    async def _analyze_character_consistency_llm(
        self,
        character_name: str,
        content: str,
        established_traits: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Use LLM to analyze character consistency
        """
        consistency_prompt = """
        Analyze character consistency for {character_name} in the provided content:
        
        Established Character Traits: {established_traits}
        
        Content to Analyze: {content}
        
        Evaluate consistency in JSON format:
        {{
            "consistency_score": 0.0-1.0,
            "consistent_elements": ["aspects that match established traits"],
            "inconsistent_elements": ["aspects that contradict established traits"],
            "issues": ["specific consistency problems found"],
            "suggestions": ["how to improve consistency"]
        }}
        """
        
        context_vars = {
            "character_name": character_name,
            "established_traits": json.dumps(established_traits),
            "content": content[:1000]  # Limit content length
        }
        
        result = await self._generate_with_llm(
            consistency_prompt,
            context_vars,
            JsonOutputParser()
        )
        
        return result
    
    async def _store_quality_assessment(
        self,
        context: AgentContext,
        quality_metrics: QualityMetrics,
        improvement_suggestions: List[str]
    ):
        """
        Store quality assessment for learning and analytics
        """
        try:
            assessment_data = {
                "story_id": str(context.story_context.story_id),
                "task_id": context.task_id,
                "quality_metrics": quality_metrics.dict(),
                "improvement_suggestions": improvement_suggestions,
                "timestamp": context.task_id
            }
            
            # Store in vector database for future reference
            await self._store_result_in_vector_db(
                content=json.dumps(assessment_data),
                metadata={
                    "story_id": str(context.story_context.story_id),
                    "agent_type": "quality_assurance",
                    "overall_score": quality_metrics.overall_quality_score,
                    "assessment_type": "full_quality_check"
                },
                collection_name="generation_embeddings"
            )
            
            # Add to local history
            self.quality_history.append(assessment_data)
            
        except Exception as e:
            logger.warning(f"Failed to store quality assessment: {e}")
