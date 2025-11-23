from PyPDF2 import PdfReader
from typing import List, Dict
import sys
import os
from Hybridrag import config
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)



class DocumentProcessor:
    def __init__(self):
        self.chunk_size = config.CHUNK_SIZE
        self.chunk_overlap = config.CHUNK_OVERLAP
    
    def extract_text_from_pdf(self, pdf_file) -> str:
        """Extract text from PDF file"""
        try:
            pdf_reader = PdfReader(pdf_file)
            text = ""
            total_pages = len(pdf_reader.pages)
            print(f"📄 PDF has {total_pages} pages")
            
            # Show progress for large documents
            progress_interval = max(1, total_pages // 10)  # Show progress every 10%
            
            for i, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                if (i + 1) % progress_interval == 0 or i == 0 or i == total_pages - 1:
                    print(f"  Processing page {i+1}/{total_pages} ({len(page_text)} chars)")
                text += page_text + "\n"
            
            print(f"✓ Total text extracted: {len(text):,} characters from {total_pages} pages")
            
            if len(text) < 100:
                print("⚠️ WARNING: Very little text extracted! PDF might be scanned images.")
            
            return text
        except Exception as e:
            print(f"❌ Error extracting text from PDF: {e}")
            raise
    
    def chunk_text(self, text: str) -> List[Dict]:
        """Split text into chunks with overlap"""
        chunks = []
        
        # Clean text
        text = text.replace('\n', ' ').replace('\r', ' ')
        text = ' '.join(text.split())  # Remove extra whitespace
        
        if len(text) < 50:
            print("⚠️ Warning: Text is very short!")
            return [{
                'content': text,
                'metadata': {'chunk_index': 0, 'chunk_size': len(text)}
            }]
        
        # Split into chunks
        start = 0
        chunk_index = 0
        
        while start < len(text):
            # Get chunk
            end = start + self.chunk_size
            chunk_text = text[start:end]
            
            # Try to break at sentence end
            if end < len(text):
                # Look for sentence ending
                last_period = chunk_text.rfind('. ')
                last_question = chunk_text.rfind('? ')
                last_exclaim = chunk_text.rfind('! ')
                
                best_break = max(last_period, last_question, last_exclaim)
                
                if best_break > self.chunk_size * 0.5:  # At least 50% of chunk size
                    chunk_text = chunk_text[:best_break + 2]
                    end = start + best_break + 2
            
            if chunk_text.strip():
                chunks.append({
                    'content': chunk_text.strip(),
                    'metadata': {
                        'chunk_index': chunk_index,
                        'chunk_size': len(chunk_text),
                        'start_char': start,
                        'end_char': end
                    }
                })
                chunk_index += 1
            
            # Move to next chunk with overlap
            start = end - self.chunk_overlap
        
        print(f"✓ Created {len(chunks)} chunks")
        
        if len(chunks) == 0:
            print("❌ ERROR: No chunks created!")
            return []
        
        # Show sample chunks
        num_samples = min(3, len(chunks))
        for i in range(num_samples):
            chunk = chunks[i]
            print(f"  Chunk {i}: {len(chunk['content'])} chars - {chunk['content'][:100]}...")
        
        if len(chunks) > 3:
            print(f"  ... and {len(chunks) - 3} more chunks")
        
        return chunks
    
    def process_pdf(self, pdf_file) -> List[Dict]:
        """Process PDF and return chunks"""
        print("\n" + "="*50)
        print("📄 Starting PDF Processing")
        print("="*50)
        
        text = self.extract_text_from_pdf(pdf_file)
        chunks = self.chunk_text(text)
        
        print(f"\n✓ Processed PDF into {len(chunks)} chunks")
        print("="*50 + "\n")
        
        return chunks