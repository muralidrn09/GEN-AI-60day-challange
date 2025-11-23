# Hybrid RAG System Setup Guide

## Prerequisites
- Python 3.11+
- PostgreSQL with PGVector (Neon.tech recommended)
- Neo4j Database (can use Docker)
- OpenAI API Key

## Quick Setup

### 1. Configure Environment Variables

Copy `.env.example` to `.env` and update with your credentials:

```bash
cp .env.example .env
```

Then edit `.env` file with your actual credentials:

**Required Configuration:**

#### OpenAI API Key
Get your API key from: https://platform.openai.com/api-keys
```
OPENAI_API_KEY=sk-proj-your-actual-api-key-here
```

#### Neon Database Connection
1. Go to https://neon.tech and create a free account
2. Create a new project
3. Enable the PGVector extension in your database
4. Copy your connection string (it will look like this):
```
NEON_CONNECTION_STRING=postgresql://username:password@ep-cool-river-123456.us-east-2.aws.neon.tech/neondb?sslmode=require
```

#### Neo4j Database
**Option 1: Docker (Easiest)**
```bash
docker run -d \
  --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/your-password-here \
  neo4j:latest
```

**Option 2: Neo4j Desktop**
Download from: https://neo4j.com/download/

Then update your `.env`:
```
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-password-here
```

### 2. Install Dependencies

Activate your virtual environment and install packages:
```bash
.\subject_venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3. Run the Application

```bash
.\subject_venv\Scripts\python.exe -m streamlit run streamlit\app.py
```

The app will open in your browser at http://localhost:8501

## Configuration Check

If you see the error "ep-your-endpoint.neon.tech", it means you haven't updated your Neon connection string yet. Make sure to:

1. Create a `.env` file (copy from `.env.example`)
2. Replace all placeholder values with your actual credentials
3. Restart the Streamlit app

## Troubleshooting

### Database Connection Errors
- **Neon**: Make sure your connection string is correct and includes the full endpoint URL
- **Neo4j**: Ensure Neo4j is running (check with `docker ps` if using Docker)

### Module Import Errors
- Make sure you're using the virtual environment's Python: `.\subject_venv\Scripts\python.exe`
- Reinstall dependencies: `pip install -r requirements.txt`

### API Key Errors
- Verify your OpenAI API key is valid
- Check you have credits available in your OpenAI account

## Features

- **Vector Store**: Uses PGVector for semantic search
- **Knowledge Graph**: Uses Neo4j for relationship-based queries
- **Hybrid RAG**: Combines both approaches for accurate, hallucination-free responses
- **PDF Processing**: Upload and process PDF documents
- **Interactive Chat**: Ask questions about your documents

## Support

For issues, please check:
1. All environment variables are correctly set in `.env`
2. All services (Neon, Neo4j) are running
3. Virtual environment is activated
4. All dependencies are installed
