"""
Utility helper functions for the knowledge management system.
"""
import os
import sys
import logging
import colorama
from typing import Dict, Any, List
from datetime import datetime

# Initialize colorama for cross-platform colored terminal output
colorama.init()

def setup_logging(log_level=logging.INFO):
    """
    Set up logging configuration.
    
    Args:
        log_level: Logging level (default: INFO)
    """
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(stream=sys.stdout)
        ]
    )

def print_colored(text: str, color: str = 'white', bold: bool = False) -> None:
    """
    Print colored text to the terminal.
    
    Args:
        text: Text to print
        color: Color name ('red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white')
        bold: Whether to use bold text
    """
    color_map = {
        'red': colorama.Fore.RED,
        'green': colorama.Fore.GREEN,
        'yellow': colorama.Fore.YELLOW,
        'blue': colorama.Fore.BLUE,
        'magenta': colorama.Fore.MAGENTA,
        'cyan': colorama.Fore.CYAN,
        'white': colorama.Fore.WHITE,
    }
    
    style = colorama.Style.BRIGHT if bold else ''
    color_code = color_map.get(color.lower(), colorama.Fore.WHITE)
    
    print(f"{style}{color_code}{text}{colorama.Style.RESET_ALL}")

def format_sources(sources: List[Dict[str, str]]) -> str:
    """
    Format source information into a readable string.
    
    Args:
        sources: List of source dictionaries
        
    Returns:
        Formatted sources string
    """
    if not sources:
        return "No sources found"
        
    source_text = "Sources:\n"
    for i, source in enumerate(sources, 1):
        source_text += f"{i}. {source['source']}\n"
    
    return source_text

def validate_file_exists(file_path: str) -> bool:
    """
    Validate that a file exists.
    
    Args:
        file_path: Path to the file
        
    Returns:
        True if the file exists, False otherwise
    """
    if not os.path.isfile(file_path):
        print_colored(f"Error: File '{file_path}' does not exist.", "red")
        return False
    return True

def format_timestamp(timestamp: float) -> str:
    """
    Format a timestamp into a readable string.
    
    Args:
        timestamp: Unix timestamp
        
    Returns:
        Formatted date/time string
    """
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime('%Y-%m-%d %H:%M:%S')