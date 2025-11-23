import psycopg2
import psycopg2.extras
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import numpy as np
from openai import OpenAI
from typing import List, Dict
import os
import sys
import Hybridrag.config as config
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

class VectorStore:
    def __init__(self):
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.conn = None
        self.setup_database()
    
    def setup_database(self):
        """Initialize PostgreSQL connection and setup pgvector"""
        try:
            self.conn = psycopg2.connect(config.NEON_CONNECTION_STRING)
            self.conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = self.conn.cursor()
            
            # Enable pgvector extension
            cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            
            # Create table for document chunks
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS document_chunks (
                    id SERIAL PRIMARY KEY,
                    content TEXT,
                    embedding vector(1536),
                    metadata JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Create index for faster similarity search
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS embedding_idx 
                ON document_chunks 
                USING ivfflat (embedding vector_cosine_ops)
                WITH (lists = 100);
            """)
            
            cursor.close()
            print("✓ Vector database initialized successfully")
        except Exception as e:
            print(f"✗ Error setting up vector database: {e}")
            raise
    
    def get_embedding(self, text: str) -> List[float]:
        """Generate embedding using OpenAI"""
        try:
            response = self.client.embeddings.create(
                model=config.EMBEDDING_MODEL,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            raise
    
    def add_documents(self, chunks: List[Dict]):
        """Add document chunks to vector store"""
        cursor = self.conn.cursor()
        added_count = 0
        failed_count = 0
        
        for i, chunk in enumerate(chunks, 1):
            try:
                print(f"Processing chunk {i}/{len(chunks)}...")
                embedding = self.get_embedding(chunk['content'])
                cursor.execute("""
                    INSERT INTO document_chunks (content, embedding, metadata)
                    VALUES (%s, %s, %s)
                """, (
                    chunk['content'],
                    embedding,
                    psycopg2.extras.Json(chunk.get('metadata', {}))
                ))
                added_count += 1
                print(f"✓ Chunk {i} added successfully")
            except Exception as e:
                failed_count += 1
                print(f"✗ Error adding chunk {i}: {str(e)}")
                # Don't stop on error, continue with next chunk
                continue
        
        self.conn.commit()
        cursor.close()
        print(f"\n✓ Successfully added {added_count}/{len(chunks)} chunks to vector store")
        if failed_count > 0:
            print(f"✗ Failed to add {failed_count} chunks")

    
    def similarity_search(self, query: str, k: int = 5) -> List[Dict]:
        """Perform similarity search"""
        try:
            query_embedding = self.get_embedding(query)
            cursor = self.conn.cursor()
            
            cursor.execute("""
                SELECT content, metadata, 
                       1 - (embedding <=> %s::vector) as similarity
                FROM document_chunks
                ORDER BY embedding <=> %s::vector
                LIMIT %s
            """, (query_embedding, query_embedding, k))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'content': row[0],
                    'metadata': row[1],
                    'similarity': float(row[2])
                })
            
            cursor.close()
            return results
        except Exception as e:
            print(f"Error in similarity search: {e}")
            return []
    
    def query(self, question: str, temperature: float = 0.3) -> Dict:
        """Query the vector store and get LLM response"""
        # Get relevant chunks
        relevant_chunks = self.similarity_search(question, k=config.TOP_K_RESULTS)
        
        if not relevant_chunks:
            return {
                'answer': "No relevant information found in the vector store.",
                'sources': [],
                'confidence': 0.0
            }
        
        # Prepare context
        context = "\n\n".join([chunk['content'] for chunk in relevant_chunks])
        
        # Generate answer using OpenAI
        try:
            response = self.client.chat.completions.create(
                model=config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": """You are a knowledgeable educational assistant helping students understand textbook content.

IMPORTANT INSTRUCTIONS:
1. Analyze the provided context carefully - it contains excerpts from educational materials
2. Answer questions directly and helpfully based on ANY relevant information in the context
3. Look for: chapter titles, unit names, topics, concepts, examples, exercises, subject matter
4. Even if the context is partial or fragmented, extract and explain the useful information present
5. For questions about topics/contents: identify subjects, units, themes, or concepts mentioned
6. Be informative and educational - help the student learn from whatever context is available
7. Only say "information not found" if the context is completely unrelated or empty

Answer naturally as if explaining to a student."""},
                    {"role": "user", "content": f"Based on this textbook excerpt:\n\n{context}\n\nQuestion: {question}\n\nAnswer:"}
                ],
                temperature=temperature,
                max_tokens=500
            )
            
            answer = response.choices[0].message.content
            avg_similarity = np.mean([chunk['similarity'] for chunk in relevant_chunks])
            
            return {
                'answer': answer,
                'sources': relevant_chunks,
                'confidence': float(avg_similarity)
            }
        except Exception as e:
            return {
                'answer': f"Error generating answer: {e}",
                'sources': relevant_chunks,
                'confidence': 0.0
            }
    
    def clear_database(self):
        """Clear all documents from vector store"""
        cursor = self.conn.cursor()
        cursor.execute("TRUNCATE TABLE document_chunks;")
        self.conn.commit()
        cursor.close()
        print("✓ Vector store cleared")
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()