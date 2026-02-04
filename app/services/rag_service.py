from typing import List, Dict
import logging
from app.services.crawler import WebCrawler
from app.services.embeddings import EmbeddingService
from app.services.vector_db import VectorDatabase
from app.services.llm import LLMService
from app.utils.chunker import TextChunker
from app.config import settings

logger = logging.getLogger(__name__)


class RAGService:
    """Main RAG service that orchestrates crawling, indexing, and querying."""
    
    def __init__(self):
        self.crawler = None
        self.chunker = TextChunker(chunk_size=500, chunk_overlap=50)
        self.embedding_service = EmbeddingService()
        self.vector_db = VectorDatabase()
        self.llm_service = LLMService()
    
    def crawl_and_index(self, url: str, max_pages: int = None) -> Dict:
        """
        Crawl a website and index its content.
        
        Args:
            url: The starting URL to crawl
            max_pages: Maximum number of pages to crawl
            
        Returns:
            Dictionary with crawl results
        """
        logger.info(f"Starting crawl and index for: {url}")
        
        # Initialize crawler
        max_pages = max_pages or settings.max_pages
        self.crawler = WebCrawler(max_pages=max_pages, max_depth=settings.crawl_depth)
        
        # Crawl the website
        pages = self.crawler.crawl(url)
        pages_crawled = len(pages)
        
        if pages_crawled == 0:
            raise ValueError("No pages were successfully crawled")
        
        # Chunk the documents
        chunks = self.chunker.chunk_documents(pages)
        
        if not chunks:
            raise ValueError("No text chunks were created from crawled pages")
        
        # Generate embeddings
        texts = [chunk['text'] for chunk in chunks]
        embeddings = self.embedding_service.generate_embeddings(texts)
        
        # Store in vector database
        pages_indexed = self.vector_db.add_documents(chunks, embeddings)
        
        logger.info(f"Indexing complete. Pages: {pages_crawled}, Chunks: {pages_indexed}")
        
        return {
            'pages_crawled': pages_crawled,
            'pages_indexed': pages_indexed,
            'website_url': url
        }
    
    def query(self, question: str, top_k: int = 5) -> Dict:
        """
        Query the RAG system with a question.
        
        Args:
            question: The user's question
            top_k: Number of relevant chunks to retrieve
            
        Returns:
            Dictionary with answer and sources
        """
        logger.info(f"Processing query: {question}")
        
        # Check if database has data
        if not self.vector_db.is_initialized():
            raise ValueError("No data in the database. Please crawl and index a website first.")
        
        # Generate embedding for the question
        question_embedding = self.embedding_service.generate_embedding(question)
        
        # Retrieve relevant chunks
        results = self.vector_db.query(question_embedding, top_k=top_k)
        
        if not results['documents']:
            return {
                'answer': "I couldn't find any relevant information to answer your question.",
                'sources': []
            }
        
        # Prepare context chunks for LLM
        context_chunks = []
        for doc, metadata, distance in zip(
            results['documents'],
            results['metadatas'],
            results['distances']
        ):
            context_chunks.append({
                'document': doc,
                'metadata': metadata,
                'distance': distance
            })
        
        # Generate answer using LLM
        answer = self.llm_service.generate_answer(question, context_chunks)
        
        # Prepare sources for response
        sources = []
        for chunk in context_chunks:
            metadata = chunk['metadata']
            # Convert distance to similarity score (cosine distance -> similarity)
            similarity = 1 - chunk['distance']
            
            sources.append({
                'url': metadata.get('url', 'Unknown'),
                'title': metadata.get('title', 'Untitled'),
                'chunk_text': chunk['document'][:200] + '...',  # First 200 chars
                'similarity_score': round(similarity, 4)
            })
        
        return {
            'answer': answer,
            'sources': sources,
            'model_used': settings.chat_model
        }
    
    def get_stats(self) -> Dict:
        """Get statistics about the indexed data."""
        return self.vector_db.get_stats()
    
    def clear_database(self) -> None:
        """Clear all data from the database."""
        self.vector_db.clear()
    
    def reindex(self, clear_existing: bool = False) -> int:
        """
        Reindex existing data (placeholder for future enhancement).
        
        Args:
            clear_existing: Whether to clear existing data
            
        Returns:
            Number of chunks reindexed
        """
        if clear_existing:
            self.clear_database()
            return 0
        
        # For now, just return current count
        stats = self.get_stats()
        return stats.get('total_chunks', 0)
    
    def health_check(self) -> Dict:
        """Check the health of all services."""
        return {
            'openai_configured': bool(settings.openai_api_key),
            'chroma_initialized': self.vector_db.is_initialized()
        }
