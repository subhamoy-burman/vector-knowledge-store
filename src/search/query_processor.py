"""
Query processor for handling search queries.
"""
import logging
from typing import Dict, Any, List, Optional

from src.search.vector_store import VectorStore
from src.utilities.helpers import print_colored, format_sources

logger = logging.getLogger(__name__)

class QueryProcessor:
    """Process and handle user queries."""
    
    def __init__(self):
        """Initialize the query processor."""
        self.vector_store = VectorStore()
    
    def process_query(self, query: str, filter_conditions: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a user query and generate an answer.
        
        Args:
            query: The user's question
            filter_conditions: Optional OData filter condition for search
            
        Returns:
            Dictionary with answer and metadata
        """
        try:
            # Search for relevant document chunks
            search_results = self.vector_store.search(query, filter_conditions)
            
            if not search_results:
                return {
                    "answer": "I couldn't find any relevant information in your knowledge base to answer this question.",
                    "sources": []
                }
                
            # Get answer from Azure OpenAI using the search results as context
            result = self.vector_store.get_answer(query, search_results)
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            raise
    
    def display_results(self, result: Dict[str, Any], show_sources: bool = True) -> None:
        """
        Display search results to the user.
        
        Args:
            result: The search result dictionary
            show_sources: Whether to show sources
        """
        if not result or "answer" not in result:
            print_colored("No results found.", "yellow")
            return
            
        # Display the answer
        print_colored("\nAnswer:", "cyan", bold=True)
        print(result["answer"])
        
        # Display sources if requested
        if show_sources and "sources" in result and result["sources"]:
            print_colored("\nSources:", "cyan", bold=True)
            for i, source in enumerate(result["sources"], 1):
                print_colored(f"{i}. {source['source']}", "yellow")