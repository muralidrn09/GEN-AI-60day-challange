from neo4j import GraphDatabase
from openai import OpenAI
from typing import List, Dict
import json
import Hybridrag.config as config
import os
import sys

# Add the parent directory to sys.path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

class KnowledgeGraph:
    def __init__(self):
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.driver = None
        self.connect()
    
    def connect(self):
        """Connect to Neo4j database"""
        try:
            self.driver = GraphDatabase.driver(
                config.NEO4J_URI,
                auth=(config.NEO4J_USER, config.NEO4J_PASSWORD)
            )
            # Test connection
            with self.driver.session() as session:
                session.run("RETURN 1")
            print("✓ Knowledge graph connected successfully")
        except Exception as e:
            print(f"✗ Error connecting to Neo4j: {e}")
            raise
    
    def extract_entities_and_relations(self, text: str) -> Dict:
        """Extract entities and relationships using GPT-4o-mini"""
        try:
            response = self.client.chat.completions.create(
                model=config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": """Extract entities and relationships from the text. 
                    Return a JSON with:
                    {
                        "entities": [{"name": "entity_name", "type": "entity_type", "properties": {}}],
                        "relationships": [{"from": "entity1", "to": "entity2", "type": "relationship_type"}]
                    }
                    Entity types can be: Person, Organization, Concept, Location, Event, etc.
                    Relationship types can be: RELATED_TO, PART_OF, BELONGS_TO, CREATED_BY, etc."""},
                    {"role": "user", "content": f"Extract entities and relationships from:\n\n{text}"}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
        except Exception as e:
            print(f"Error extracting entities: {e}")
            return {"entities": [], "relationships": []}
    
    def add_documents(self, chunks: List[Dict]):
        """Add document chunks to knowledge graph"""
        processed_count = 0
        failed_count = 0
        
        with self.driver.session() as session:
            for idx, chunk in enumerate(chunks):
                try:
                    print(f"Processing chunk {idx+1}/{len(chunks)}...")
                    
                    # Extract entities and relationships
                    extracted = self.extract_entities_and_relations(chunk['content'])
                    print(f"  Found {len(extracted.get('entities', []))} entities and {len(extracted.get('relationships', []))} relationships")
                    
                    # Create document node
                    session.run("""
                        MERGE (d:Document {id: $doc_id})
                        SET d.content = $content,
                            d.chunk_index = $idx
                    """, doc_id=f"doc_{idx}", content=chunk['content'], idx=idx)
                    
                    # Create entity nodes
                    for entity in extracted.get('entities', []):
                        session.run("""
                            MERGE (e:Entity {name: $name})
                            SET e.type = $type,
                                e.properties = $properties
                            WITH e
                            MATCH (d:Document {id: $doc_id})
                            MERGE (d)-[:CONTAINS]->(e)
                        """, 
                        name=entity['name'],
                        type=entity.get('type', 'Unknown'),
                        properties=json.dumps(entity.get('properties', {})),
                        doc_id=f"doc_{idx}"
                        )
                    
                    # Create relationships
                    for rel in extracted.get('relationships', []):
                        session.run("""
                            MATCH (e1:Entity {name: $from_entity})
                            MATCH (e2:Entity {name: $to_entity})
                            MERGE (e1)-[r:RELATIONSHIP {type: $rel_type}]->(e2)
                        """,
                        from_entity=rel['from'],
                        to_entity=rel['to'],
                        rel_type=rel.get('type', 'RELATED_TO')
                        )
                    
                    processed_count += 1
                    print(f"✓ Chunk {idx+1} processed successfully")
                except Exception as e:
                    failed_count += 1
                    print(f"✗ Error processing chunk {idx+1}: {e}")
        
        print(f"\n✓ Knowledge Graph Summary:")
        print(f"  - Successful: {processed_count}")
        print(f"  - Failed: {failed_count}")
        print(f"  - Total: {len(chunks)}")
    
    def query_graph(self, question: str) -> List[Dict]:
        """Query the knowledge graph"""
        try:
            # Extract key entities from question
            response = self.client.chat.completions.create(
                model=config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "Extract the main entities or concepts from the question. Return them as a JSON array of strings."},
                    {"role": "user", "content": question}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            entities_data = json.loads(response.choices[0].message.content)
            query_entities = entities_data.get('entities', [])
            
            if not query_entities:
                query_entities = question.split()[:3]  # Fallback to first 3 words
            
            results = []
            with self.driver.session() as session:
                for entity in query_entities:
                    # Find related information
                    cypher_query = """
                        MATCH (e:Entity)
                        WHERE toLower(e.name) CONTAINS toLower($entity)
                        OPTIONAL MATCH (e)-[r]-(related:Entity)
                        OPTIONAL MATCH (d:Document)-[:CONTAINS]->(e)
                        RETURN e.name as entity, 
                               e.type as type,
                               collect(DISTINCT related.name) as related_entities,
                               collect(DISTINCT d.content) as documents
                        LIMIT 5
                    """
                    
                    result = session.run(cypher_query, entity=entity)
                    for record in result:
                        results.append({
                            'entity': record['entity'],
                            'type': record['type'],
                            'related_entities': record['related_entities'],
                            'documents': record['documents']
                        })
            
            return results
        except Exception as e:
            print(f"Error querying graph: {e}")
            return []
    
    def query(self, question: str, temperature: float = 0.3) -> Dict:
        """Query knowledge graph and generate answer"""
        graph_results = self.query_graph(question)
        
        if not graph_results:
            return {
                'answer': "No relevant information found in the knowledge graph.",
                'entities': [],
                'confidence': 0.0
            }
        
        # Prepare context from graph results
        context_parts = []
        for result in graph_results:
            context_parts.append(f"Entity: {result['entity']} (Type: {result['type']})")
            if result['related_entities']:
                context_parts.append(f"Related to: {', '.join(result['related_entities'])}")
            if result['documents']:
                for doc in result['documents'][:2]:  # Limit to 2 documents per entity
                    if doc:
                        context_parts.append(f"Context: {doc}")
        
        context = "\n".join(context_parts)
        
        # Generate answer
        try:
            response = self.client.chat.completions.create(
                model=config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": """You are an educational assistant using a knowledge graph to help students.

INSTRUCTIONS:
1. Use the entities and relationships provided to answer the question
2. Explain connections between concepts, topics, and related subjects
3. Even with limited graph data, provide helpful information about what entities and relationships are present
4. Be informative and educational about the topics mentioned
5. Connect related concepts to give a comprehensive answer

Answer naturally and helpfully based on the knowledge graph information."""},
                    {"role": "user", "content": f"Knowledge Graph Information:\n{context}\n\nQuestion: {question}\n\nAnswer:"}
                ],
                temperature=temperature,
                max_tokens=500
            )
            
            answer = response.choices[0].message.content
            
            return {
                'answer': answer,
                'entities': graph_results,
                'confidence': 0.8 if graph_results else 0.0
            }
        except Exception as e:
            return {
                'answer': f"Error generating answer: {e}",
                'entities': graph_results,
                'confidence': 0.0
            }
    
    def clear_database(self):
        """Clear all data from knowledge graph"""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
        print("✓ Knowledge graph cleared")
    
    def close(self):
        """Close Neo4j connection"""
        if self.driver:
            self.driver.close()