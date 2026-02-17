import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional
import logging
from datetime import datetime
import os
from app.config import settings

logger = logging.getLogger(__name__)


class VectorDatabase:
    """Service to manage ChromaDB vector database."""
    
    def __init__(self):
        """Initialize ChromaDB client."""
        # Create persist directory if it doesn't exist
        os.makedirs(settings.chroma_persist_directory, exist_ok=True)
        
        # Initialize ChromaDB client with persistence
        self.client = chromadb.PersistentClient(
            path=settings.chroma_persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        self.collection_name = "rag_documents"
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        
        logger.info(f"ChromaDB initialized. Collection: {self.collection_name}")
    
    def add_documents(
        self,
        chunks: List[Dict],
        embeddings: List[List[float]]
    ) -> int:
        """
        Add documents to the vector database.
        
        Args:
            chunks: List of chunk dictionaries with text and metadata
            embeddings: List of embedding vectors
            
        Returns:
            Number of documents added
        """
        if not chunks or not embeddings:
            logger.warning("No chunks or embeddings to add")
            return 0
        
        if len(chunks) != len(embeddings):
            raise ValueError("Number of chunks must match number of embeddings")
        
        # Prepare data for ChromaDB
        ids = [f"doc_{i}_{datetime.now().timestamp()}" for i in range(len(chunks))]
        documents = [chunk['text'] for chunk in chunks]
        metadatas = []
        
        for chunk in chunks:
            metadata = chunk.get('metadata', {})
            # ChromaDB requires metadata values to be strings, ints, floats, or bools
            clean_metadata = {
                'url': str(metadata.get('url', '')),
                'title': str(metadata.get('title', '')),
                'token_count': int(chunk.get('token_count', 0)),
                'indexed_at': datetime.now().isoformat()
            }
            metadatas.append(clean_metadata)
        
        # Add to collection
        try:
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas
            )
            logger.info(f"Added {len(chunks)} documents to vector database")
            return len(chunks)
        except Exception as e:
            logger.error(f"Error adding documents to database: {str(e)}")
            raise
    
    def query(
        self,
        query_embedding: List[float],
        top_k: int = 5
    ) -> Dict:
        """
        Query the vector database for similar documents.
        
        Args:
            query_embedding: The query embedding vector
            top_k: Number of results to return
            
        Returns:
            Dictionary with results
        """
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )
            
            # Format results
            formatted_results = {
                'documents': results['documents'][0] if results['documents'] else [],
                'metadatas': results['metadatas'][0] if results['metadatas'] else [],
                'distances': results['distances'][0] if results['distances'] else []
            }
            
            logger.info(f"Retrieved {len(formatted_results['documents'])} results")
            return formatted_results
        except Exception as e:
            logger.error(f"Error querying database: {str(e)}")
            raise
    
    def get_stats(self) -> Dict:
        """Get database statistics."""
        try:
            count = self.collection.count()
            
            # Get unique URLs
            if count > 0:
                results = self.collection.get()
                urls = set()
                last_indexed = None
                
                if results['metadatas']:
                    for metadata in results['metadatas']:
                        if 'url' in metadata:
                            # Extract base URL
                            url = metadata['url'].split('?')[0].split('#')[0]
                            base_url = '/'.join(url.split('/')[:3])
                            urls.add(base_url)
                        
                        # Track last indexed time
                        if 'indexed_at' in metadata:
                            indexed_time = datetime.fromisoformat(metadata['indexed_at'])
                            if last_indexed is None or indexed_time > last_indexed:
                                last_indexed = indexed_time
                
                unique_urls = list(urls)
            else:
                unique_urls = []
                last_indexed = None
            
            # Calculate database size
            db_size_mb = 0
            if os.path.exists(settings.chroma_persist_directory):
                for root, dirs, files in os.walk(settings.chroma_persist_directory):
                    db_size_mb += sum(os.path.getsize(os.path.join(root, f)) for f in files)
                db_size_mb = db_size_mb / (1024 * 1024)  # Convert to MB
            
            return {
                'total_chunks': count,
                'indexed_websites': unique_urls,
                'database_size_mb': round(db_size_mb, 2),
                'last_indexed': last_indexed
            }
        except Exception as e:
            logger.error(f"Error getting stats: {str(e)}")
            raise
    
    def clear(self) -> None:
        """Clear all documents from the database."""
        try:
            # Delete and recreate collection
            self.client.delete_collection(name=self.collection_name)
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info("Database cleared successfully")
        except Exception as e:
            logger.error(f"Error clearing database: {str(e)}")
            raise
    
    def is_initialized(self) -> bool:
        """Check if database is initialized and has data."""
        try:
            return self.collection.count() > 0
        except Exception:
            return False
