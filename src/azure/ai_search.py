"""
Azure AI Search service for vector search.
"""
import logging
import json
from typing import List, Dict, Any, Optional

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.models import VectorizedQuery

from config.settings import (
    AZURE_SEARCH_ENDPOINT,
    AZURE_SEARCH_KEY,
    AZURE_SEARCH_INDEX_NAME,
    EMBEDDING_DIMENSION,
    TOP_K_RESULTS,
    SIMILARITY_THRESHOLD
)

logger = logging.getLogger(__name__)

class AzureSearchService:
    """Service for Azure AI Search operations."""
    
    def __init__(self):
        """Initialize Azure AI Search clients."""
        self.endpoint = AZURE_SEARCH_ENDPOINT
        self.key = AZURE_SEARCH_KEY
        self.index_name = AZURE_SEARCH_INDEX_NAME
        self.credential = AzureKeyCredential(self.key)
        
        # Clients
        self.index_client = SearchIndexClient(
            endpoint=self.endpoint,
            credential=self.credential
        )
        self.search_client = SearchClient(
            endpoint=self.endpoint,
            index_name=self.index_name,
            credential=self.credential
        )
    
    def create_index_if_not_exists(self) -> None:
        """Create the search index if it doesn't exist."""
        from azure.search.documents.indexes.models import (
            SearchIndex,
            SimpleField,
            SearchableField,
            SearchFieldDataType,
            VectorSearch,
            VectorSearchProfile,
            HnswAlgorithmConfiguration
        )
        
        # Check if index already exists
        if self.index_name in [index.name for index in self.index_client.list_indexes()]:
            logger.info(f"Index '{self.index_name}' already exists")
            return
            
        # Define vector search configuration
        vector_search = VectorSearch(
            profiles=[
                VectorSearchProfile(
                    name="vector-profile",
                    algorithm_configuration_name="hnsw-config"
                )
            ],
            algorithms=[
                HnswAlgorithmConfiguration(
                    name="hnsw-config",
                    parameters={
                        "m": 4,
                        "efConstruction": 400,
                        "efSearch": 500,
                        "metric": "cosine"
                    }
                )
            ]
        )
        
        # Define fields for the search index
        fields = [
            SimpleField(name="id", type=SearchFieldDataType.String, key=True),
            SimpleField(name="chunk_id", type=SearchFieldDataType.Int32),
            SearchableField(name="text", type=SearchFieldDataType.String),
            SimpleField(name="source", type=SearchFieldDataType.String, filterable=True),
            SimpleField(name="path", type=SearchFieldDataType.String),
            SimpleField(name="document_type", type=SearchFieldDataType.String, filterable=True),
            SimpleField(name="created", type=SearchFieldDataType.DateTimeOffset, filterable=True, sortable=True),
            SimpleField(name="modified", type=SearchFieldDataType.DateTimeOffset, filterable=True, sortable=True),
            SimpleField(
                name="embedding",
                type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                vector_search_dimensions=EMBEDDING_DIMENSION,
                vector_search_profile_name="vector-profile"
            )
        ]
        
        # Create the index
        index = SearchIndex(name=self.index_name, fields=fields, vector_search=vector_search)
        self.index_client.create_index(index)
        logger.info(f"Created index '{self.index_name}'")
    
    def index_documents(self, documents: List[Dict[str, Any]]) -> None:
        """
        Index documents in Azure AI Search.
        
        Args:
            documents: List of document chunks with embeddings
        """
        try:
            # Make sure index exists
            self.create_index_if_not_exists()
            
            # Upload documents in batches to avoid size limits
            batch_size = 100
            for i in range(0, len(documents), batch_size):
                batch = documents[i:i+batch_size]
                results = self.search_client.upload_documents(documents=batch)
                success_count = sum(1 for r in results if r.succeeded)
                logger.info(f"Indexed {success_count}/{len(batch)} document chunks")
                
        except Exception as e:
            logger.error(f"Error indexing documents: {e}")
            raise
    
    def vector_search(self, query_vector: List[float], filter_conditions: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Perform vector search using query embedding.
        
        Args:
            query_vector: The embedding vector of the query
            filter_conditions: Optional OData filter expression
            
        Returns:
            List of search results
        """
        try:
            vector_query = VectorizedQuery(vector=query_vector, k_nearest_neighbors=TOP_K_RESULTS, fields="embedding")
            
            results = self.search_client.search(
                search_text=None,
                vector_queries=[vector_query],
                filter=filter_conditions,
                select=["id", "text", "source", "path", "document_type", "@search.score"]
            )
            
            search_results = []
            for result in results:
                # Only include results above similarity threshold
                if result["@search.score"] >= SIMILARITY_THRESHOLD:
                    search_results.append({
                        "id": result["id"],
                        "text": result["text"],
                        "source": result["source"],
                        "path": result["path"],
                        "document_type": result["document_type"],
                        "score": result["@search.score"]
                    })
            
            return search_results
            
        except Exception as e:
            logger.error(f"Error in vector search: {e}")
            raise