"""
Vector store module to handle search operations.
"""
import logging
from typing import List, Dict, Any, Optional

from src.azure.openai_service import AzureOpenAIService
from src.azure.ai_search import AzureSearchService

logger = logging.getLogger(__name__)

class VectorStore:
    """Vector store for document retrieval and search."""
    
    def __init__(self):
        """Initialize the vector store services."""
        self.search_service = AzureSearchService()
        self.openai_service = AzureOpenAIService()
    
    def ingest_documents(self, document_chunks: List[Dict[str, Any]]) -> None:
        """
        Ingest document chunks into the vector store.
        
        Args:
            document_chunks: List of document chunks with embeddings
        """
        try:
            # First, ensure the index exists
            self.search_service.create_index_if_not_exists()
            
            # Then, upload the documents to the index
            self.search_service.index_documents(document_chunks)
            
        except Exception as e:
            logger.error(f"Error ingesting documents into vector store: {e}")
            raise
    
    def search(self, query: str, filter_conditions: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search the vector store with a query.
        
        Args:
            query: The search query
            filter_conditions: Optional OData filter conditions
            
        Returns:
            List of search results
        """
        try:
            # Generate embedding for the query
            query_embedding = self.openai_service.generate_embeddings([query])[0]
            
            # Perform vector search
            results = self.search_service.vector_search(query_embedding, filter_conditions)
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching vector store: {e}")
            raise
    
    def get_answer(self, query: str, context: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate an answer based on the query and context.
        
        Args:
            query: The user's question
            context: Retrieved document chunks
            
        Returns:
            Answer and sources
        """
        try:
            return self.openai_service.generate_answer(query, context)
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            raise