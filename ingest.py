#!/usr/bin/env python
"""
Document ingestion script for the Personal Knowledge Management System.

Usage:
    python ingest.py --file path/to/document.pdf
    python ingest.py --dir path/to/directory
"""
import os
import sys
import argparse
import logging
from pathlib import Path
from typing import List, Dict, Any

from src.utilities.helpers import setup_logging, print_colored, validate_file_exists
from src.ingestion.document_loader import DocumentLoader
from src.ingestion.text_processor import TextProcessor
from src.ingestion.embeddings import EmbeddingGenerator
from src.azure.blob_storage import BlobStorageService
from src.search.vector_store import VectorStore

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Ingest documents into the knowledge base")
    
    # Add mutually exclusive group for file or directory
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--file', '-f', type=str, help="Path to the document file to ingest")
    group.add_argument('--dir', '-d', type=str, help="Path to a directory of documents to ingest")
    
    # Add optional arguments
    parser.add_argument('--skip-upload', action='store_true', help="Skip uploading to blob storage")
    parser.add_argument('--verbose', '-v', action='store_true', help="Enable verbose logging")
    
    return parser.parse_args()

def ingest_file(file_path: str, skip_upload: bool = False) -> Dict[str, Any]:
    """
    Ingest a single document file.
    
    Args:
        file_path: Path to the document file
        skip_upload: Whether to skip uploading to blob storage
        
    Returns:
        Dictionary with ingestion metadata
    """
    print_colored(f"Ingesting file: {file_path}", "cyan")
    
    # 1. Load the document
    document_loader = DocumentLoader()
    document = document_loader.load_document(file_path)
    print_colored(f"Loaded document: {document['source']}", "green")
    
    # 2. Process and chunk the text
    text_processor = TextProcessor()
    document_chunks = text_processor.process_document(document)
    print_colored(f"Created {len(document_chunks)} text chunks", "green")
    
    # 3. Generate embeddings
    embedding_generator = EmbeddingGenerator()
    document_chunks_with_embeddings = embedding_generator.generate_embeddings(document_chunks)
    print_colored("Generated embeddings for all chunks", "green")
    
    # 4. Upload to blob storage (unless skipped)
    if not skip_upload:
        blob_service = BlobStorageService()
        blob_metadata = blob_service.upload_file(file_path)
        print_colored(f"Uploaded to blob storage: {blob_metadata['blob_name']}", "green")
    
    # 5. Store in vector index
    vector_store = VectorStore()
    vector_store.ingest_documents(document_chunks_with_embeddings)
    print_colored("Indexed in vector store", "green")
    
    return {
        "file": document["source"],
        "chunks": len(document_chunks),
        "status": "success"
    }

def ingest_directory(dir_path: str, skip_upload: bool = False) -> List[Dict[str, Any]]:
    """
    Ingest all supported documents in a directory.
    
    Args:
        dir_path: Path to the directory
        skip_upload: Whether to skip uploading to blob storage
        
    Returns:
        List of dictionaries with ingestion metadata
    """
    print_colored(f"Ingesting documents from directory: {dir_path}", "cyan")
    
    # Check if directory exists
    if not os.path.isdir(dir_path):
        print_colored(f"Error: Directory '{dir_path}' does not exist.", "red")
        return []
    
    # Get all supported files in directory
    supported_extensions = ['.pdf', '.docx', '.doc', '.txt', '.md']
    files = []
    
    for ext in supported_extensions:
        files.extend(list(Path(dir_path).glob(f"**/*{ext}")))
    
    if not files:
        print_colored(f"No supported documents found in '{dir_path}'", "yellow")
        return []
    
    # Ingest each file
    results = []
    for file_path in files:
        try:
            result = ingest_file(str(file_path), skip_upload)
            results.append(result)
        except Exception as e:
            print_colored(f"Error ingesting {file_path}: {str(e)}", "red")
            results.append({
                "file": str(file_path),
                "status": "error",
                "error": str(e)
            })
    
    return results

def main():
    """Main function to run document ingestion."""
    # Parse arguments
    args = parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    setup_logging(log_level)
    
    print_colored("Starting document ingestion...", "blue", bold=True)
    
    try:
        # Process file or directory based on arguments
        if args.file:
            if validate_file_exists(args.file):
                result = ingest_file(args.file, args.skip_upload)
                if result["status"] == "success":
                    print_colored(f"✅ Successfully ingested {result['file']} with {result['chunks']} chunks", "green", bold=True)
                else:
                    print_colored(f"❌ Failed to ingest {result['file']}", "red", bold=True)
        
        elif args.dir:
            results = ingest_directory(args.dir, args.skip_upload)
            
            # Print summary
            success_count = sum(1 for r in results if r["status"] == "success")
            print_colored(f"\n✅ Successfully ingested {success_count} out of {len(results)} documents", "green", bold=True)
            
            if success_count < len(results):
                print_colored(f"❌ Failed to ingest {len(results) - success_count} documents", "red", bold=True)
        
    except Exception as e:
        print_colored(f"Error: {str(e)}", "red", bold=True)
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())