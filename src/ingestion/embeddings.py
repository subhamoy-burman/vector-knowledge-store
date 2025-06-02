"""
Generate embeddings for document chunks using Azure OpenAI.
"""
import logging
import numpy as np
from typing import List, Dict, Any, Union

from openai import AzureOpenAI
from config.settings import (
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_KEY,
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
    AZURE_OPENAI_API_VERSION
)

logger = logging.getLogger(__name__)

class EmbeddingGenerator:
    """Generate embeddings using Azure OpenAI."""
    
    def __init__(self):
        """Initialize the Azure OpenAI client."""
        self.client = AzureOpenAI(
            api_key=AZURE_OPENAI_KEY,
            api_version=AZURE_OPENAI_API_VERSION,
            azure_endpoint=AZURE_OPENAI_ENDPOINT
        )
        self.deployment = AZURE_OPENAI_EMBEDDING_DEPLOYMENT
    
    def generate_embeddings(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate embeddings for a list of document chunks.
        
        Args:
            chunks: List of document chunks with text and metadata
            
        Returns:
            List of document chunks with embeddings added
        """
        texts = [chunk["text"] for chunk in chunks]
        
        try:
            embeddings = self._get_embeddings(texts)
            
            # Add embeddings to chunks
            for i, chunk in enumerate(chunks):
                chunk["embedding"] = embeddings[i]
            
            return chunks
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise
    
    def _get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Get embeddings for a list of texts using Azure OpenAI.
        
        Args:
            texts: List of text strings
            
        Returns:
            List of embedding vectors as floats
        """
        # Process in batches to avoid token limits
        batch_size = 16
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            response = self.client.embeddings.create(
                input=batch,
                model=self.deployment
            )
            batch_embeddings = [item.embedding for item in response.data]
            all_embeddings.extend(batch_embeddings)
        
        return all_embeddings