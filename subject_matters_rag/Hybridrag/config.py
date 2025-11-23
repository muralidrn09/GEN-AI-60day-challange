import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", " Your open AI key ")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Neon PostgreSQL with PGVector Configuration
NEON_CONNECTION_STRING = os.getenv(
    "NEON_CONNECTION_STRING",
    "postgresql://neondb_owner:npg_b4ySdB2VtUhk@ep-long-frog-ah6zxxdm-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
)

# Neo4j Configuration (Docker)
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "knowledge_graph_demo_2024")

# Embedding Configuration
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", "1536"))

# RAG Configuration
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))
TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", "15"))  # Increased to 15 for better context retrieval