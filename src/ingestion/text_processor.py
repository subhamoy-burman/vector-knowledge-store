"""
Text processor for chunking and preparing document text.
"""
import re
import uuid
from typing import Dict, List, Any

from config.settings import CHUNK_SIZE, CHUNK_OVERLAP

class TextProcessor:
    """Process and chunk document text for embeddings."""
    
    @staticmethod
    def process_document(document: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        Process a document by chunking its text content.
        
        Args:
            document: Document dictionary with metadata and text
            
        Returns:
            List of document chunks with metadata
        """
        chunks = TextProcessor._chunk_text(document["text"])
        
        # Create document chunks with metadata
        document_chunks = []
        for i, chunk_text in enumerate(chunks):
            chunk_id = str(uuid.uuid4())
            document_chunks.append({
                "id": chunk_id,
                "chunk_id": i,
                "text": chunk_text,
                "source": document["source"],
                "path": document["path"],
                "document_type": document.get("type", "unknown"),
                "created": document.get("created"),
                "modified": document.get("modified")
            })
        
        return document_chunks
    
    @staticmethod
    def _chunk_text(text: str) -> List[str]:
        """
        Split text into chunks with overlap.
        
        Args:
            text: The document text to chunk
            
        Returns:
            List of text chunks
        """
        if not text:
            return []
            
        # Normalize line breaks and remove excessive whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r'\s{2,}', ' ', text)
        
        # Simple chunking by character count with overlap
        chunks = []
        start = 0
        
        while start < len(text):
            # Find a good breakpoint near CHUNK_SIZE
            end = start + CHUNK_SIZE
            
            if end >= len(text):
                # Last chunk
                chunks.append(text[start:])
                break
                
            # Try to find sentence boundary for cleaner breaks
            sentence_end = TextProcessor._find_sentence_end(text, end)
            if sentence_end > start:  # Ensure we don't create empty chunks
                chunks.append(text[start:sentence_end])
                start = sentence_end - CHUNK_OVERLAP
            else:
                # Fall back to word boundary if no sentence boundary found
                word_end = TextProcessor._find_word_end(text, end)
                chunks.append(text[start:word_end])
                start = word_end - CHUNK_OVERLAP
                
        return chunks
    
    @staticmethod
    def _find_sentence_end(text: str, position: int) -> int:
        """Find the nearest sentence end after the given position."""
        # Look for common sentence enders within a window after position
        search_window = min(position + 100, len(text))
        
        for pattern in [r'\.', r'\!', r'\?', r'\n\n']:
            matches = list(re.finditer(pattern, text[position:search_window]))
            if matches:
                return position + matches[0].end()
        
        return position
    
    @staticmethod
    def _find_word_end(text: str, position: int) -> int:
        """Find the nearest word end after the given position."""
        if position >= len(text):
            return len(text)
            
        # Find next space or fall back to position if none found
        next_space = text.find(' ', position, min(position + 50, len(text)))
        return next_space + 1 if next_space != -1 else position