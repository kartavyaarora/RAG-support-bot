from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class CrawlRequest(BaseModel):
    """Request model for crawling a website."""
    url: HttpUrl = Field(..., description="The URL of the website to crawl")
    max_pages: Optional[int] = Field(default=100, description="Maximum number of pages to crawl", ge=1, le=500)
    
    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://docs.python.org/3/",
                "max_pages": 50
            }
        }


class CrawlResponse(BaseModel):
    """Response model for crawl operation."""
    status: str
    message: str
    pages_crawled: int
    pages_indexed: int
    website_url: str
    timestamp: datetime = Field(default_factory=datetime.now)


class QueryRequest(BaseModel):
    """Request model for querying the RAG system."""
    question: str = Field(..., description="The question to ask", min_length=1)
    top_k: Optional[int] = Field(default=5, description="Number of relevant chunks to retrieve", ge=1, le=20)
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "How do I install Python packages?",
                "top_k": 5
            }
        }


class Source(BaseModel):
    """Source information for a retrieved chunk."""
    url: str
    title: Optional[str] = None
    chunk_text: str
    similarity_score: float


class QueryResponse(BaseModel):
    """Response model for query operation."""
    answer: str
    sources: List[Source]
    question: str
    model_used: str
    timestamp: datetime = Field(default_factory=datetime.now)


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str
    timestamp: datetime = Field(default_factory=datetime.now)
    version: str = "1.0.0"
    openai_configured: bool
    chroma_initialized: bool


class StatsResponse(BaseModel):
    """Response model for statistics."""
    total_documents: int
    total_chunks: int
    indexed_websites: List[str]
    database_size_mb: float
    last_indexed: Optional[datetime] = None
    

class ReindexRequest(BaseModel):
    """Request model for reindexing."""
    clear_existing: bool = Field(default=False, description="Whether to clear existing data before reindexing")


class ReindexResponse(BaseModel):
    """Response model for reindex operation."""
    status: str
    message: str
    chunks_reindexed: int
    timestamp: datetime = Field(default_factory=datetime.now)


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
