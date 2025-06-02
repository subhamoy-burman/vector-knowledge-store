#!/usr/bin/env python
"""
Environment test script to verify dependencies and Azure services.
"""
import os
import sys
import importlib
import logging
from dotenv import load_dotenv

def check_module(module_name):
    """Check if a Python module is installed."""
    try:
        importlib.import_module(module_name)
        return True
    except ImportError:
        return False

def check_azure_env_vars():
    """Check if Azure environment variables are set."""
    # Load .env file if it exists
    if os.path.exists(".env"):
        load_dotenv()
    
    # Required Azure environment variables
    azure_vars = [
        "AZURE_STORAGE_CONNECTION_STRING",
        "AZURE_SEARCH_ENDPOINT",
        "AZURE_SEARCH_KEY",
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_KEY",
        "AZURE_OPENAI_DEPLOYMENT",
        "AZURE_OPENAI_EMBEDDING_DEPLOYMENT"
    ]
    
    missing_vars = []
    for var in azure_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    return {
        "total": len(azure_vars),
        "missing": missing_vars,
        "configured": len(azure_vars) - len(missing_vars)
    }

def print_result(name, status, message=None):
    """Print a formatted check result."""
    status_str = "✅" if status else "❌"
    
    if message:
        print(f"{status_str} {name}: {message}")
    else:
        print(f"{status_str} {name}")

def main():
    """Run tests to verify environment setup."""
    print("Personal Knowledge Management System - Environment Test")
    print("=" * 60)
    
    # Check Python version
    py_version = sys.version.split()[0]
    is_compatible = sys.version_info >= (3, 8)
    print_result(
        "Python version", 
        is_compatible,
        f"{py_version} {'(Compatible)' if is_compatible else '(Incompatible - need 3.8+)'}"
    )
    
    # Check required packages
    required_modules = [
        "azure.storage.blob",
        "azure.search.documents",
        "openai",
        "dotenv",
        "PyPDF2",
        "docx",
        "tiktoken",
        "langchain",
        "pydantic",
        "numpy",
        "tqdm",
        "colorama"
    ]
    
    print("\nChecking required packages:")
    missing_modules = []
    for module in required_modules:
        is_installed = check_module(module)
        if not is_installed:
            missing_modules.append(module)
        print_result(f"  {module}", is_installed)
    
    # Check Azure environment variables
    print("\nChecking Azure configuration:")
    env_result = check_azure_env_vars()
    
    if env_result["missing"]:
        print_result(
            "Azure environment variables",
            False,
            f"{env_result['configured']}/{env_result['total']} configured"
        )
        print("\nMissing environment variables:")
        for var in env_result["missing"]:
            print(f"  - {var}")
        print("\nPlease configure these variables in a .env file.")
    else:
        print_result(
            "Azure environment variables",
            True,
            "All required variables configured"
        )
    
    # Check directory structure
    print("\nChecking directory structure:")
    directories = [
        "config",
        "data/temp",
        "src/ingestion",
        "src/search",
        "src/azure",
        "src/utilities"
    ]
    
    missing_dirs = []
    for directory in directories:
        exists = os.path.isdir(directory)
        if not exists:
            missing_dirs.append(directory)
        print_result(f"  {directory}", exists)
    
    # Summary
    print("\n" + "=" * 60)
    if missing_modules or env_result["missing"] or missing_dirs:
        print("❌ Environment setup incomplete. Please address the issues above.")
        return 1
    else:
        print("✅ Environment setup complete! You're ready to start using the system.")
        print("\nTry these commands:")
        print("  - To ingest a document: python ingest.py --file your_document.pdf")
        print("  - To query your knowledge: python query.py \"Your question here?\"")
        print("  - For interactive queries: python query.py --interactive")
        return 0

if __name__ == "__main__":
    sys.exit(main())
