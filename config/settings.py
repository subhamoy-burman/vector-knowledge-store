"""
Configuration settings for the Personal Knowledge Management System.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Azure Blob Storage settings
AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
BLOB_CONTAINER_NAME = os.getenv("BLOB_CONTAINER_NAME", "documents")

# Azure AI Search settings
AZURE_SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
AZURE_SEARCH_KEY = os.getenv("AZURE_SEARCH_KEY")
AZURE_SEARCH_INDEX_NAME = os.getenv("AZURE_SEARCH_INDEX_NAME", "knowledge-index")

# Azure OpenAI settings
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2023-07-01-preview")
AZURE_OPENAI_EMBEDDING_DEPLOYMENT = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")

# Text processing settings
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
EMBEDDING_DIMENSION = 1536  # Dimension of Azure OpenAI embeddings

# Search settings
TOP_K_RESULTS = 5
SIMILARITY_THRESHOLD = 0.7

# System prompts
SYSTEM_PROMPT = """You are a helpful assistant that answers questions based on the provided context.
Only use information from the context to answer the question.
If you don't know the answer, say "I don't have enough information to answer this question." 
Keep your answers concise and to the point."""