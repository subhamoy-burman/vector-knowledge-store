#!/usr/bin/env python
"""
Query script for the Personal Knowledge Management System.

Usage:
    python query.py "Your question here?"
    python query.py --interactive
"""
import sys
import argparse
import logging
from typing import Optional

from src.utilities.helpers import setup_logging, print_colored
from src.search.query_processor import QueryProcessor

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Query the knowledge base")
    
    # Add mutually exclusive group for query or interactive mode
    group = parser.add_mutually_exclusive_group()
    group.add_argument('query', nargs='?', type=str, help="The question to ask the knowledge base")
    group.add_argument('--interactive', '-i', action='store_true', help="Start interactive query mode")
    
    # Add optional arguments
    parser.add_argument('--no-sources', action='store_true', help="Don't show source documents")
    parser.add_argument('--filter', '-f', type=str, help="Filter results (e.g., 'document_type eq pdf')")
    parser.add_argument('--verbose', '-v', action='store_true', help="Enable verbose logging")
    
    return parser.parse_args()

def process_query(query: str, filter_condition: Optional[str] = None, show_sources: bool = True):
    """
    Process a single query.
    
    Args:
        query: The user's question
        filter_condition: Optional OData filter expression
        show_sources: Whether to show source documents
    """
    query_processor = QueryProcessor()
    
    print_colored(f"Question: {query}", "blue", bold=True)
    
    try:
        # Process the query
        result = query_processor.process_query(query, filter_condition)
        
        # Display results
        query_processor.display_results(result, show_sources)
        
    except Exception as e:
        print_colored(f"Error: {str(e)}", "red")

def interactive_mode(show_sources: bool = True):
    """
    Start interactive query mode.
    
    Args:
        show_sources: Whether to show source documents
    """
    print_colored("Interactive Query Mode", "blue", bold=True)
    print_colored("Enter your questions and get answers from your knowledge base.", "cyan")
    print_colored("Type 'exit', 'quit', or Ctrl+C to exit.", "cyan")
    
    query_processor = QueryProcessor()
    
    while True:
        try:
            # Get user input
            print_colored("\nQuestion: ", "blue", bold=True)
            query = input()
            
            # Check for exit command
            if query.lower() in ["exit", "quit"]:
                print_colored("Exiting interactive mode.", "yellow")
                break
            
            # Skip empty queries
            if not query.strip():
                continue
                
            # Process the query
            result = query_processor.process_query(query)
            
            # Display results
            query_processor.display_results(result, show_sources)
            
        except KeyboardInterrupt:
            print_colored("\nExiting interactive mode.", "yellow")
            break
        except Exception as e:
            print_colored(f"Error: {str(e)}", "red")

def main():
    """Main function to run the query script."""
    # Parse arguments
    args = parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    setup_logging(log_level)
    
    try:
        # Determine mode of operation
        if args.interactive:
            interactive_mode(not args.no_sources)
        elif args.query:
            process_query(args.query, args.filter, not args.no_sources)
        else:
            print_colored("Error: Please provide a query or use --interactive mode", "red")
            return 1
            
    except Exception as e:
        print_colored(f"Error: {str(e)}", "red", bold=True)
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())