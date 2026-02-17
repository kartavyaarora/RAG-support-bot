import tiktoken
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class TextChunker:
    """Utility to chunk text into smaller pieces for embedding."""
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        """
        Initialize the text chunker.
        
        Args:
            chunk_size: Maximum number of tokens per chunk
            chunk_overlap: Number of tokens to overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.encoding = tiktoken.get_encoding("cl100k_base")  # Used by OpenAI models
    
    def count_tokens(self, text: str) -> int:
        """Count the number of tokens in a text."""
        return len(self.encoding.encode(text))
    
    def chunk_text(self, text: str, metadata: Dict = None) -> List[Dict]:
        """
        Split text into chunks with overlap.
        
        Args:
            text: The text to chunk
            metadata: Optional metadata to attach to each chunk
            
        Returns:
            List of dictionaries containing chunk text and metadata
        """
        if not text or not text.strip():
            return []
        
        # Encode the text
        tokens = self.encoding.encode(text)
        chunks = []
        
        # Split into chunks with overlap
        start = 0
        while start < len(tokens):
            # Get chunk
            end = start + self.chunk_size
            chunk_tokens = tokens[start:end]
            
            # Decode back to text
            chunk_text = self.encoding.decode(chunk_tokens)
            
            # Create chunk dictionary
            chunk_data = {
                'text': chunk_text,
                'token_count': len(chunk_tokens)
            }
            
            # Add metadata if provided
            if metadata:
                chunk_data['metadata'] = metadata
            
            chunks.append(chunk_data)
            
            # Move to next chunk with overlap
            if end >= len(tokens):
                break
            start = end - self.chunk_overlap
        
        logger.debug(f"Split text into {len(chunks)} chunks")
        return chunks
    
    def chunk_documents(self, documents: List[Dict[str, str]]) -> List[Dict]:
        """
        Chunk multiple documents.
        
        Args:
            documents: List of documents with 'content', 'url', and 'title'
            
        Returns:
            List of chunked documents with metadata
        """
        all_chunks = []
        
        for doc in documents:
            content = doc.get('content', '')
            url = doc.get('url', '')
            title = doc.get('title', '')
            
            if not content:
                continue
            
            metadata = {
                'url': url,
                'title': title
            }
            
            chunks = self.chunk_text(content, metadata)
            all_chunks.extend(chunks)
        
        logger.info(f"Created {len(all_chunks)} chunks from {len(documents)} documents")
        return all_chunks
