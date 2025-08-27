# services/vector_service.py
import pinecone
from openai import OpenAI
from typing import Dict, Any, List, Optional, Union
import json
import logging
import uuid
import asyncio
from datetime import datetime
import numpy as np

from config.settings import settings, VECTOR_COLLECTIONS

logger = logging.getLogger(__name__)

class VectorService:
    """
    Vector database service using Pinecone for semantic search and context management.
    Handles embedding storage, retrieval, and similarity search for story elements.
    """
    
    def __init__(self):
        self.pinecone_index = None
        self.openai_client = None
        self.initialized = False
        
    async def initialize(self):
        """Initialize Pinecone and OpenAI clients"""
        try:
            # Initialize OpenAI client for embeddings
            if not settings.openai_api_key:
                raise Exception("OpenAI API key not found. Please set OPENAI_API_KEY in your environment.")
            
            self.openai_client = OpenAI(api_key=settings.openai_api_key)
            
            # Initialize Pinecone
            if not settings.pinecone_api_key:
                raise Exception("Pinecone API key not found. Please set PINECONE_API_KEY in your environment.")
            
            pinecone.init(
                api_key=settings.pinecone_api_key,
                environment=settings.pinecone_environment
            )
            
            # Get or create index
            index_name = settings.pinecone_index_name
            if index_name not in pinecone.list_indexes():
                # Create index if it doesn't exist
                pinecone.create_index(
                    name=index_name,
                    dimension=1536,  # OpenAI text-embedding-ada-002 dimension
                    metric="cosine"
                )
                logger.info(f"Created Pinecone index: {index_name}")
            
            self.pinecone_index = pinecone.Index(index_name)
            
            self.initialized = True
            logger.info("Vector service initialized successfully with Pinecone and OpenAI")
            
        except Exception as e:
            logger.error(f"Failed to initialize vector service: {e}")
            raise
    
    async def _get_embedding(self, text: str) -> List[float]:
        """Get embedding for text using OpenAI"""
        try:
            response = self.openai_client.embeddings.create(
                model="text-embedding-ada-002",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Failed to get embedding: {e}")
            raise
    
    async def store_embedding(
        self,
        collection_name: str,
        text: str,
        metadata: Dict[str, Any],
        document_id: Optional[str] = None
    ) -> str:
        """
        Store text with embedding in Pinecone
        
        Args:
            collection_name: Name of the collection (used as namespace in Pinecone)
            text: Text content to embed and store
            metadata: Metadata to associate with the embedding
            document_id: Optional custom document ID
            
        Returns:
            Document ID of stored embedding
        """
        if not self.initialized:
            await self.initialize()
        
        if document_id is None:
            document_id = str(uuid.uuid4())
        
        try:
            # Get embedding
            embedding = await self._get_embedding(text)
            
            # Add timestamp to metadata
            metadata["timestamp"] = datetime.utcnow().isoformat()
            metadata["text_length"] = len(text)
            metadata["collection"] = collection_name
            
            # Store in Pinecone
            self.pinecone_index.upsert(
                vectors=[(document_id, embedding, metadata)],
                namespace=collection_name
            )
            
            logger.debug(f"Stored embedding in {collection_name} with ID: {document_id}")
            return document_id
            
        except Exception as e:
            logger.error(f"Failed to store embedding: {e}")
            raise
    
    async def search_similar(
        self,
        collection_name: str,
        query_text: str,
        n_results: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None,
        include_distances: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents in Pinecone
        
        Args:
            collection_name: Collection (namespace) to search in
            query_text: Query text to find similar documents for
            n_results: Number of results to return
            filter_metadata: Optional metadata filters
            include_distances: Whether to include similarity distances
            
        Returns:
            List of similar documents with metadata
        """
        if not self.initialized:
            await self.initialize()
        
        try:
            # Get query embedding
            query_embedding = await self._get_embedding(query_text)
            
            # Prepare query parameters
            query_params = {
                "vector": query_embedding,
                "top_k": n_results,
                "namespace": collection_name,
                "include_metadata": True
            }
            
            if include_distances:
                query_params["include_values"] = True
            
            # Add metadata filter if provided
            if filter_metadata:
                query_params["filter"] = filter_metadata
            
            # Perform search
            results = self.pinecone_index.query(**query_params)
            
            # Format results
            formatted_results = []
            for match in results.matches:
                result = {
                    "content": match.metadata.get("text", ""),  # Store original text in metadata
                    "metadata": match.metadata,
                    "id": match.id
                }
                
                if include_distances:
                    result["similarity_score"] = match.score
                
                formatted_results.append(result)
            
            logger.debug(f"Found {len(formatted_results)} similar documents in {collection_name}")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Failed to search similar documents: {e}")
            return []
    
    async def get_by_id(
        self,
        collection_name: str,
        document_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get document by ID from Pinecone
        
        Args:
            collection_name: Collection (namespace) to search in
            document_id: ID of document to retrieve
            
        Returns:
            Document data or None if not found
        """
        if not self.initialized:
            await self.initialize()
        
        try:
            results = self.pinecone_index.fetch(
                ids=[document_id],
                namespace=collection_name
            )
            
            if document_id in results.vectors:
                vector_data = results.vectors[document_id]
                return {
                    "id": document_id,
                    "content": vector_data.metadata.get("text", ""),
                    "metadata": vector_data.metadata,
                    "values": vector_data.values
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get document by ID: {e}")
            return None
    
    async def update_document(
        self,
        collection_name: str,
        document_id: str,
        text: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Update existing document in Pinecone
        
        Args:
            collection_name: Collection (namespace) containing the document
            document_id: ID of document to update
            text: New text content (optional)
            metadata: New metadata (optional)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.initialized:
            await self.initialize()
        
        try:
            # Get existing document
            existing = await self.get_by_id(collection_name, document_id)
            if not existing:
                return False
            
            # Prepare update data
            update_metadata = existing["metadata"].copy()
            if metadata:
                update_metadata.update(metadata)
            
            update_metadata["updated_at"] = datetime.utcnow().isoformat()
            
            # If text changed, get new embedding
            if text and text != existing["content"]:
                new_embedding = await self._get_embedding(text)
                update_metadata["text"] = text
                update_metadata["text_length"] = len(text)
                
                # Upsert with new embedding
                self.pinecone_index.upsert(
                    vectors=[(document_id, new_embedding, update_metadata)],
                    namespace=collection_name
                )
            else:
                # Update metadata only
                self.pinecone_index.update(
                    id=document_id,
                    set_metadata=update_metadata,
                    namespace=collection_name
                )
            
            logger.debug(f"Updated document {document_id} in {collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update document: {e}")
            return False
    
    async def delete_document(
        self,
        collection_name: str,
        document_id: str
    ) -> bool:
        """
        Delete document from Pinecone
        
        Args:
            collection_name: Collection (namespace) containing the document
            document_id: ID of document to delete
            
        Returns:
            True if successful, False otherwise
        """
        if not self.initialized:
            await self.initialize()
        
        try:
            self.pinecone_index.delete(
                ids=[document_id],
                namespace=collection_name
            )
            
            logger.debug(f"Deleted document {document_id} from {collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete document: {e}")
            return False
    
    async def get_collection_stats(self, collection_name: str) -> Dict[str, Any]:
        """
        Get statistics for a collection (namespace)
        
        Args:
            collection_name: Name of collection (namespace)
            
        Returns:
            Collection statistics
        """
        if not self.initialized:
            await self.initialize()
        
        try:
            # Get index stats
            index_stats = self.pinecone_index.describe_index_stats()
            
            # Get namespace stats
            namespace_stats = index_stats.namespaces.get(collection_name, {})
            
            stats = {
                "document_count": namespace_stats.get("vector_count", 0),
                "collection_name": collection_name,
                "dimension": index_stats.dimension,
                "metric": index_stats.metric,
                "total_vector_count": index_stats.total_vector_count
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            return {"error": str(e)}
    
    async def search_by_metadata(
        self,
        collection_name: str,
        metadata_filter: Dict[str, Any],
        n_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search documents by metadata filters only
        
        Args:
            collection_name: Collection (namespace) to search in
            metadata_filter: Metadata filter conditions
            n_results: Number of results to return
            
        Returns:
            List of matching documents
        """
        if not self.initialized:
            await self.initialize()
        
        try:
            # Use a dummy vector for metadata-only search
            dummy_vector = [0.0] * 1536  # OpenAI embedding dimension
            
            results = self.pinecone_index.query(
                vector=dummy_vector,
                top_k=n_results,
                namespace=collection_name,
                filter=metadata_filter,
                include_metadata=True
            )
            
            formatted_results = []
            for match in results.matches:
                formatted_results.append({
                    "content": match.metadata.get("text", ""),
                    "metadata": match.metadata,
                    "id": match.id,
                    "similarity_score": match.score
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Failed to search by metadata: {e}")
            return []
    
    async def batch_store_embeddings(
        self,
        collection_name: str,
        documents: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Store multiple documents in batch for efficiency
        
        Args:
            collection_name: Collection (namespace) to store in
            documents: List of documents with 'text', 'metadata', and optional 'id'
            
        Returns:
            List of document IDs
        """
        if not self.initialized:
            await self.initialize()
        
        try:
            # Get embeddings for all texts
            texts = [doc["text"] for doc in documents]
            embeddings = await self._batch_get_embeddings(texts)
            
            # Prepare vectors for Pinecone
            vectors = []
            for i, doc in enumerate(documents):
                doc_id = doc.get("id", str(uuid.uuid4()))
                
                metadata = doc.get("metadata", {}).copy()
                metadata["timestamp"] = datetime.utcnow().isoformat()
                metadata["text_length"] = len(doc["text"])
                metadata["collection"] = collection_name
                metadata["text"] = doc["text"]  # Store original text
                
                vectors.append((doc_id, embeddings[i], metadata))
            
            # Batch upsert
            self.pinecone_index.upsert(
                vectors=vectors,
                namespace=collection_name
            )
            
            logger.info(f"Batch stored {len(documents)} documents in {collection_name}")
            return [doc.get("id", str(uuid.uuid4())) for doc in documents]
            
        except Exception as e:
            logger.error(f"Failed to batch store embeddings: {e}")
            raise
    
    async def _batch_get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings for multiple texts using OpenAI"""
        try:
            response = self.openai_client.embeddings.create(
                model="text-embedding-ada-002",
                input=texts
            )
            return [data.embedding for data in response.data]
        except Exception as e:
            logger.error(f"Failed to get batch embeddings: {e}")
            raise
    
    async def semantic_search_across_collections(
        self,
        query_text: str,
        collection_names: List[str],
        n_results_per_collection: int = 3,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Search across multiple collections and return combined results
        
        Args:
            query_text: Query text
            collection_names: List of collections (namespaces) to search
            n_results_per_collection: Results per collection
            filter_metadata: Optional metadata filter
            
        Returns:
            Dictionary with collection names as keys and results as values
        """
        results = {}
        
        for collection_name in collection_names:
            try:
                collection_results = await self.search_similar(
                    collection_name=collection_name,
                    query_text=query_text,
                    n_results=n_results_per_collection,
                    filter_metadata=filter_metadata
                )
                results[collection_name] = collection_results
                
            except Exception as e:
                logger.warning(f"Failed to search collection {collection_name}: {e}")
                results[collection_name] = []
        
        return results
    
    async def cleanup_old_embeddings(
        self,
        collection_name: str,
        days_old: int = 30
    ) -> int:
        """
        Clean up old embeddings based on timestamp
        
        Args:
            collection_name: Collection (namespace) to clean up
            days_old: Delete embeddings older than this many days
            
        Returns:
            Number of documents deleted
        """
        if not self.initialized:
            await self.initialize()
        
        try:
            from datetime import timedelta
            cutoff = datetime.utcnow() - timedelta(days=days_old)
            cutoff_iso = cutoff.isoformat()
            
            # Search for old documents
            old_docs = await self.search_by_metadata(
                collection_name=collection_name,
                metadata_filter={
                    "timestamp": {"$lt": cutoff_iso}
                },
                n_results=1000  # Adjust based on your needs
            )
            
            if old_docs:
                old_doc_ids = [doc["id"] for doc in old_docs]
                self.pinecone_index.delete(
                    ids=old_doc_ids,
                    namespace=collection_name
                )
                logger.info(f"Cleaned up {len(old_doc_ids)} old documents from {collection_name}")
                return len(old_doc_ids)
            
            return 0
            
        except Exception as e:
            logger.error(f"Failed to cleanup old embeddings: {e}")
            return 0
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on vector service
        
        Returns:
            Health status information
        """
        try:
            if not self.initialized:
                await self.initialize()
            
            # Test OpenAI embeddings
            test_embedding = await self._get_embedding("health check")
            
            # Get index stats
            index_stats = self.pinecone_index.describe_index_stats()
            
            # Get collection stats
            collection_stats = {}
            for name in VECTOR_COLLECTIONS.values():
                stats = await self.get_collection_stats(name)
                collection_stats[name] = stats
            
            return {
                "status": "healthy",
                "initialized": self.initialized,
                "openai_embeddings": "working",
                "pinecone_index": settings.pinecone_index_name,
                "collections": collection_stats,
                "total_vectors": index_stats.total_vector_count,
                "embedding_model": "text-embedding-ada-002"
            }
            
        except Exception as e:
            logger.error(f"Vector service health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "initialized": self.initialized
            }
    
    async def reset_collection(self, collection_name: str) -> bool:
        """
        Reset (delete all vectors) a collection (namespace)
        
        Args:
            collection_name: Collection (namespace) to reset
            
        Returns:
            True if successful
        """
        if not self.initialized:
            await self.initialize()
        
        try:
            # Delete all vectors in the namespace
            self.pinecone_index.delete(
                delete_all=True,
                namespace=collection_name
            )
            
            logger.info(f"Reset collection: {collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to reset collection {collection_name}: {e}")
            return False

# Global vector service instance
vector_service = VectorService()

# Convenience functions
async def get_vector_service() -> VectorService:
    """Get initialized vector service instance"""
    if not vector_service.initialized:
        await vector_service.initialize()
    return vector_service
