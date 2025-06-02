"""
Document loader for extracting text from various document types.
"""
import os
import logging
from pathlib import Path
from typing import Dict, Optional, List

import PyPDF2
import docx

logger = logging.getLogger(__name__)

class DocumentLoader:
    """Loads and extracts text from different document types."""
    
    @staticmethod
    def load_document(file_path: str) -> Dict[str, str]:
        """
        Load text content from a document file.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Dictionary with metadata and text content
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_name = path.name
        file_extension = path.suffix.lower()
        
        if file_extension == '.pdf':
            text = DocumentLoader._extract_text_from_pdf(file_path)
        elif file_extension in ['.docx', '.doc']:
            text = DocumentLoader._extract_text_from_word(file_path)
        elif file_extension in ['.txt', '.md', '.py', '.json', '.csv']:
            text = DocumentLoader._extract_text_from_text_file(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")
        
        return {
            "source": file_name,
            "path": file_path,
            "text": text,
            "type": file_extension.replace('.', ''),
            "created": os.path.getctime(file_path),
            "modified": os.path.getmtime(file_path)
        }
    
    @staticmethod
    def _extract_text_from_pdf(file_path: str) -> str:
        """Extract text from PDF file."""
        text = []
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page_num in range(len(reader.pages)):
                    page = reader.pages[page_num]
                    text.append(page.extract_text())
            return "\n".join(text)
        except Exception as e:
            logger.error(f"Error extracting text from PDF {file_path}: {e}")
            raise
    
    @staticmethod
    def _extract_text_from_word(file_path: str) -> str:
        """Extract text from Word document."""
        try:
            doc = docx.Document(file_path)
            text = [paragraph.text for paragraph in doc.paragraphs if paragraph.text]
            return "\n".join(text)
        except Exception as e:
            logger.error(f"Error extracting text from Word document {file_path}: {e}")
            raise
    
    @staticmethod
    def _extract_text_from_text_file(file_path: str) -> str:
        """Extract text from plain text file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            # Try alternative encodings if utf-8 fails
            with open(file_path, 'r', encoding='latin-1') as file:
                return file.read()
        except Exception as e:
            logger.error(f"Error extracting text from text file {file_path}: {e}")
            raise