"""
Azure OpenAI service for text generation and embeddings.
"""
import logging
from typing import List, Dict, Any

from openai import AzureOpenAI
from config.settings import (
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_KEY,
    AZURE_OPENAI_DEPLOYMENT,
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
    AZURE_OPENAI_API_VERSION,
    SYSTEM_PROMPT
)

logger = logging.getLogger(__name__)

class AzureOpenAIService:
    """Service for Azure OpenAI operations."""
    
    def __init__(self):
        """Initialize the Azure OpenAI client."""
        self.client = AzureOpenAI(
            api_key=AZURE_OPENAI_KEY,
            api_version=AZURE_OPENAI_API_VERSION,
            azure_endpoint=AZURE_OPENAI_ENDPOINT
        )
        self.deployment = AZURE_OPENAI_DEPLOYMENT
        self.embedding_deployment = AZURE_OPENAI_EMBEDDING_DEPLOYMENT
        self.system_prompt = SYSTEM_PROMPT
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts: List of text strings
            
        Returns:
            List of embedding vectors as floats
        """
        try:
            # Process in batches to avoid token limits
            batch_size = 16
            all_embeddings = []
            
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i+batch_size]
                response = self.client.embeddings.create(
                    input=batch,
                    model=self.embedding_deployment
                )
                batch_embeddings = [item.embedding for item in response.data]
                all_embeddings.extend(batch_embeddings)
            
            return all_embeddings
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise
    
    def generate_answer(self, query: str, context: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate an answer using retrieved context and Azure OpenAI.
        
        Args:
            query: The user's question
            context: Retrieved document chunks as context
            
        Returns:
            Dictionary with answer and metadata
        """
        try:
            # Combine context texts
            context_text = "\n\n".join([f"Source: {item['source']}\n{item['text']}" for item in context])
            
            # Create prompt
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": f"Question: {query}\n\nContext:\n{context_text}"}
            ]
            
            # Generate response
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=messages,
                temperature=0.0,
                max_tokens=500
            )
            
            answer = response.choices[0].message.content
            
            # Create sources list without duplicates
            sources = []
            for item in context:
                if item["source"] not in [src["source"] for src in sources]:
                    sources.append({
                        "source": item["source"],
                        "path": item["path"]
                    })
            
            return {
                "answer": answer,
                "sources": sources
            }
            
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            raise