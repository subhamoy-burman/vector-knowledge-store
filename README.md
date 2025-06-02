# Personal Knowledge Management System

A terminal-based system for personal knowledge management using Azure services and RAG (Retrieval-Augmented Generation).

## Features

- Ingest documents (PDF, Word, Text) into your knowledge base
- Index and search your documents using vector embeddings
- Query your knowledge base with natural language questions
- Uses Azure AI Search and Azure OpenAI for powerful retrieval and generation

## Setup

### Prerequisites

- Python 3.8+
- Azure subscription with:
  - Azure AI Search service
  - Azure Blob Storage account
  - Azure OpenAI access (GPT-4.1)

### Installation

1. Clone this repository
2. Install dependencies:
```
pip install -r requirements.txt
```
3. Create a `.env` file with your Azure credentials (see `.env.example`)

## Usage

### Ingest Documents

```
python ingest.py --file path/to/your/document.pdf
```

### Query Knowledge Base

```
python query.py "Your question here?"
```

## Configuration

Edit `config/settings.py` to adjust:

- Chunking strategy
- Embedding dimensions
- Similarity search parameters
- Other RAG settings

## Architecture

- Document ingestion pipeline: Loads documents, chunks text, generates embeddings, and stores them in Azure AI Search
- Query pipeline: Converts questions to embeddings, retrieves relevant chunks, and uses GPT-4.1 to generate answers