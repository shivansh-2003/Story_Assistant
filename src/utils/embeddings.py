# utils/embeddings.py
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer
import logging
import asyncio
from functools import lru_cache
import hashlib
import json

from config.settings import settings

logger = logging.getLogger(__name__)

class EmbeddingManager:
    """
    Centralized embedding management for text similarity and semantic search
    """
    
    def __init__(self, model_name: str = None):
        self.model_name = model_name or settings.embedding_model
        self.model = None
        self.embedding_cache: Dict[str, np.ndarray] = {}
        self.max_cache_size = 1000
        
    async def initialize(self):
        """Initialize the embedding model"""
        try:
            logger.info(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            logger.info("Embedding model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise
    
    def _get_cache_key(self, text: str) -> str:
        """Generate cache key for text"""
        return hashlib.md5(text.encode()).hexdigest()
    
    async def encode_text(self, text: str) -> np.ndarray:
        """
        Encode text to embedding vector
        
        Args:
            text: Text to encode
            
        Returns:
            Embedding vector as numpy array
        """
        if not self.model:
            await self.initialize()
        
        # Check cache first
        cache_key = self._get_cache_key(text)
        if cache_key in self.embedding_cache:
            return self.embedding_cache[cache_key]
        
        try:
            # Generate embedding
            embedding = self.model.encode(text, convert_to_numpy=True)
            
            # Cache result (with size limit)
            if len(self.embedding_cache) < self.max_cache_size:
                self.embedding_cache[cache_key] = embedding
            
            return embedding
            
        except Exception as e:
            logger.error(f"Failed to encode text: {e}")
            raise
    
    async def encode_batch(self, texts: List[str]) -> List[np.ndarray]:
        """
        Encode multiple texts in batch for efficiency
        
        Args:
            texts: List of texts to encode
            
        Returns:
            List of embedding vectors
        """
        if not self.model:
            await self.initialize()
        
        try:
            # Check for cached embeddings
            embeddings = []
            uncached_texts = []
            uncached_indices = []
            
            for i, text in enumerate(texts):
                cache_key = self._get_cache_key(text)
                if cache_key in self.embedding_cache:
                    embeddings.append(self.embedding_cache[cache_key])
                else:
                    embeddings.append(None)  # Placeholder
                    uncached_texts.append(text)
                    uncached_indices.append(i)
            
            # Generate embeddings for uncached texts
            if uncached_texts:
                new_embeddings = self.model.encode(uncached_texts, convert_to_numpy=True)
                
                # Cache and insert new embeddings
                for idx, embedding in zip(uncached_indices, new_embeddings):
                    embeddings[idx] = embedding
                    
                    # Cache if space available
                    if len(self.embedding_cache) < self.max_cache_size:
                        cache_key = self._get_cache_key(texts[idx])
                        self.embedding_cache[cache_key] = embedding
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Failed to encode batch: {e}")
            raise
    
    def calculate_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two embeddings
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Cosine similarity score (0-1)
        """
        try:
            # Normalize vectors
            norm1 = np.linalg.norm(embedding1)
            norm2 = np.linalg.norm(embedding2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            # Calculate cosine similarity
            similarity = np.dot(embedding1, embedding2) / (norm1 * norm2)
            
            # Clamp to [0, 1] range
            return max(0.0, min(1.0, float(similarity)))
            
        except Exception as e:
            logger.error(f"Failed to calculate similarity: {e}")
            return 0.0
    
    async def find_similar_texts(
        self, 
        query_text: str, 
        candidate_texts: List[str], 
        top_k: int = 5
    ) -> List[Tuple[str, float]]:
        """
        Find most similar texts to query
        
        Args:
            query_text: Query text
            candidate_texts: List of candidate texts
            top_k: Number of top results to return
            
        Returns:
            List of (text, similarity_score) tuples
        """
        try:
            # Encode query
            query_embedding = await self.encode_text(query_text)
            
            # Encode candidates
            candidate_embeddings = await self.encode_batch(candidate_texts)
            
            # Calculate similarities
            similarities = []
            for i, candidate_embedding in enumerate(candidate_embeddings):
                similarity = self.calculate_similarity(query_embedding, candidate_embedding)
                similarities.append((candidate_texts[i], similarity))
            
            # Sort by similarity and return top_k
            similarities.sort(key=lambda x: x[1], reverse=True)
            return similarities[:top_k]
            
        except Exception as e:
            logger.error(f"Failed to find similar texts: {e}")
            return []
    
    def cluster_embeddings(
        self, 
        embeddings: List[np.ndarray], 
        n_clusters: int = 5
    ) -> List[int]:
        """
        Cluster embeddings using K-means
        
        Args:
            embeddings: List of embedding vectors
            n_clusters: Number of clusters
            
        Returns:
            List of cluster labels
        """
        try:
            from sklearn.cluster import KMeans
            
            if len(embeddings) < n_clusters:
                return list(range(len(embeddings)))
            
            # Stack embeddings
            embedding_matrix = np.vstack(embeddings)
            
            # Perform clustering
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            cluster_labels = kmeans.fit_predict(embedding_matrix)
            
            return cluster_labels.tolist()
            
        except ImportError:
            logger.warning("scikit-learn not available for clustering")
            return [0] * len(embeddings)
        except Exception as e:
            logger.error(f"Failed to cluster embeddings: {e}")
            return [0] * len(embeddings)

# Character consistency utilities
class CharacterConsistencyChecker:
    """
    Check character consistency using embeddings
    """
    
    def __init__(self, embedding_manager: EmbeddingManager):
        self.embedding_manager = embedding_manager
        self.character_profiles: Dict[str, Dict[str, Any]] = {}
    
    async def store_character_profile(
        self, 
        character_id: str, 
        descriptions: List[str],
        metadata: Dict[str, Any] = None
    ):
        """
        Store character profile with embeddings
        
        Args:
            character_id: Unique character identifier
            descriptions: List of character descriptions
            metadata: Additional character metadata
        """
        try:
            # Generate embeddings for all descriptions
            embeddings = await self.embedding_manager.encode_batch(descriptions)
            
            # Calculate average embedding
            avg_embedding = np.mean(embeddings, axis=0)
            
            # Store profile
            self.character_profiles[character_id] = {
                "descriptions": descriptions,
                "embeddings": embeddings,
                "average_embedding": avg_embedding,
                "metadata": metadata or {}
            }
            
            logger.debug(f"Stored character profile for {character_id}")
            
        except Exception as e:
            logger.error(f"Failed to store character profile: {e}")
    
    async def check_consistency(
        self, 
        character_id: str, 
        new_description: str,
        threshold: float = 0.8
    ) -> Dict[str, Any]:
        """
        Check if new description is consistent with stored profile
        
        Args:
            character_id: Character identifier
            new_description: New character description
            threshold: Consistency threshold (0-1)
            
        Returns:
            Consistency check result
        """
        try:
            if character_id not in self.character_profiles:
                return {
                    "consistent": True,
                    "similarity_score": 1.0,
                    "message": "No previous profile to compare against"
                }
            
            profile = self.character_profiles[character_id]
            
            # Encode new description
            new_embedding = await self.embedding_manager.encode_text(new_description)
            
            # Calculate similarity with average profile
            similarity = self.embedding_manager.calculate_similarity(
                new_embedding, profile["average_embedding"]
            )
            
            consistent = similarity >= threshold
            
            return {
                "consistent": consistent,
                "similarity_score": similarity,
                "threshold": threshold,
                "message": "Consistent" if consistent else "Potential inconsistency detected"
            }
            
        except Exception as e:
            logger.error(f"Failed to check consistency: {e}")
            return {
                "consistent": True,
                "similarity_score": 0.0,
                "message": f"Error checking consistency: {e}"
            }

# Plot coherence utilities
class PlotCoherenceAnalyzer:
    """
    Analyze plot coherence using embeddings
    """
    
    def __init__(self, embedding_manager: EmbeddingManager):
        self.embedding_manager = embedding_manager
        self.plot_points: List[Dict[str, Any]] = []
    
    async def add_plot_point(
        self, 
        description: str, 
        chapter: int, 
        importance: int = 5,
        metadata: Dict[str, Any] = None
    ):
        """
        Add plot point for coherence tracking
        
        Args:
            description: Plot point description
            chapter: Chapter number
            importance: Importance score (1-10)
            metadata: Additional metadata
        """
        try:
            # Generate embedding
            embedding = await self.embedding_manager.encode_text(description)
            
            plot_point = {
                "description": description,
                "chapter": chapter,
                "importance": importance,
                "embedding": embedding,
                "metadata": metadata or {}
            }
            
            self.plot_points.append(plot_point)
            
        except Exception as e:
            logger.error(f"Failed to add plot point: {e}")
    
    async def analyze_coherence(self) -> Dict[str, Any]:
        """
        Analyze overall plot coherence
        
        Returns:
            Coherence analysis results
        """
        try:
            if len(self.plot_points) < 2:
                return {
                    "coherence_score": 1.0,
                    "message": "Insufficient plot points for analysis"
                }
            
            # Calculate pairwise similarities
            similarities = []
            for i in range(len(self.plot_points)):
                for j in range(i + 1, len(self.plot_points)):
                    similarity = self.embedding_manager.calculate_similarity(
                        self.plot_points[i]["embedding"],
                        self.plot_points[j]["embedding"]
                    )
                    similarities.append(similarity)
            
            # Calculate overall coherence score
            coherence_score = np.mean(similarities)
            
            # Identify potential gaps
            gaps = []
            for i in range(len(self.plot_points) - 1):
                current_chapter = self.plot_points[i]["chapter"]
                next_chapter = self.plot_points[i + 1]["chapter"]
                
                if next_chapter - current_chapter > 2:  # Gap of more than 2 chapters
                    gaps.append(f"Potential gap between chapters {current_chapter} and {next_chapter}")
            
            return {
                "coherence_score": coherence_score,
                "total_plot_points": len(self.plot_points),
                "average_similarity": coherence_score,
                "potential_gaps": gaps,
                "message": "Good coherence" if coherence_score > 0.6 else "Consider improving plot connections"
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze coherence: {e}")
            return {
                "coherence_score": 0.0,
                "message": f"Error analyzing coherence: {e}"
            }

# Global embedding manager instance
embedding_manager = EmbeddingManager()

# Convenience functions
async def get_embedding_manager() -> EmbeddingManager:
    """Get initialized embedding manager"""
    if not embedding_manager.model:
        await embedding_manager.initialize()
    return embedding_manager

@lru_cache(maxsize=100)
def preprocess_text_for_embedding(text: str) -> str:
    """
    Preprocess text for better embedding quality
    
    Args:
        text: Raw text
        
    Returns:
        Preprocessed text
    """
    # Remove excessive whitespace
    text = " ".join(text.split())
    
    # Limit length (embeddings work better with reasonable length)
    if len(text) > 1000:
        text = text[:1000] + "..."
    
    return text

async def calculate_text_similarity(text1: str, text2: str) -> float:
    """
    Calculate similarity between two texts
    
    Args:
        text1: First text
        text2: Second text
        
    Returns:
        Similarity score (0-1)
    """
    try:
        manager = await get_embedding_manager()
        
        # Preprocess texts
        text1 = preprocess_text_for_embedding(text1)
        text2 = preprocess_text_for_embedding(text2)
        
        # Generate embeddings
        embedding1 = await manager.encode_text(text1)
        embedding2 = await manager.encode_text(text2)
        
        # Calculate similarity
        return manager.calculate_similarity(embedding1, embedding2)
        
    except Exception as e:
        logger.error(f"Failed to calculate text similarity: {e}")
        return 0.0

async def find_most_relevant_context(
    query: str, 
    contexts: List[str], 
    top_k: int = 3
) -> List[Tuple[str, float]]:
    """
    Find most relevant context for a query
    
    Args:
        query: Query text
        contexts: List of context strings
        top_k: Number of top results
        
    Returns:
        List of (context, relevance_score) tuples
    """
    try:
        manager = await get_embedding_manager()
        
        # Preprocess texts
        query = preprocess_text_for_embedding(query)
        contexts = [preprocess_text_for_embedding(ctx) for ctx in contexts]
        
        # Find similar contexts
        results = await manager.find_similar_texts(query, contexts, top_k)
        
        return results
        
    except Exception as e:
        logger.error(f"Failed to find relevant context: {e}")
        return []
