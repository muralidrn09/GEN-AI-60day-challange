from Hybridrag.vector_store import VectorStore
from Hybridrag.knowledge_graph import KnowledgeGraph
from Hybridrag.document_processor import DocumentProcessor
from typing import Dict
import os
import sys

# Add the parent directory to sys.path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

class HybridRAG:
    def __init__(self):
        self.vector_store = VectorStore()
        self.knowledge_graph = KnowledgeGraph()
        self.document_processor = DocumentProcessor()
        print("✓ Hybrid RAG system initialized")
    
    def process_document(self, pdf_file):
        """Process a PDF document and add to both stores"""
        try:
            # Process PDF into chunks
            chunks = self.document_processor.process_pdf(pdf_file)
            
            # Add to vector store
            print("\n📊 Adding to Vector Store...")
            self.vector_store.add_documents(chunks)
            
            # Add to knowledge graph
            print("\n🕸️  Building Knowledge Graph...")
            self.knowledge_graph.add_documents(chunks)
            
            return {
                'success': True,
                'chunks_processed': len(chunks),
                'message': f'Successfully processed {len(chunks)} chunks'
            }
        except Exception as e:
            return {
                'success': False,
                'chunks_processed': 0,
                'message': f'Error processing document: {e}'
            }
    
    def query(self, question: str, temperature: float = 0.3) -> Dict:
        """Query both vector store and knowledge graph"""
        print(f"\n🔍 Processing query: {question}")
        
        # Query vector store
        print("📊 Querying Vector Store...")
        vector_result = self.vector_store.query(question, temperature=temperature)
        
        # Query knowledge graph
        print("🕸️  Querying Knowledge Graph...")
        graph_result = self.knowledge_graph.query(question, temperature=temperature)
        
        return {
            'question': question,
            'vector_response': vector_result,
            'graph_response': graph_result
        }
    
    def clear_all(self):
        """Clear both stores"""
        self.vector_store.clear_database()
        self.knowledge_graph.clear_database()
        print("✓ All data cleared")
    
    def close(self):
        """Close all connections"""
        self.vector_store.close()
        self.knowledge_graph.close()
        print("✓ Connections closed")