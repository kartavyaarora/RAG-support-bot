from fastapi import APIRouter, HTTPException, status
from datetime import datetime
import logging
from app.models import (
    CrawlRequest,
    CrawlResponse,
    QueryRequest,
    QueryResponse,
    HealthResponse,
    StatsResponse,
    ReindexRequest,
    ReindexResponse,
    ErrorResponse
)
from app.services.rag_service import RAGService

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Initialize RAG service (singleton)
rag_service = RAGService()


@router.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "message": "RAG Q&A Support Bot API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "crawl": "/crawl (POST)",
            "query": "/query (POST)",
            "stats": "/stats",
            "reindex": "/reindex (POST)",
            "clear": "/clear (POST)"
        },
        "documentation": "/docs"
    }


@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Check the health status of the API and its services.
    
    Returns:
        HealthResponse with status and service checks
    """
    try:
        health = rag_service.health_check()
        
        return HealthResponse(
            status="healthy",
            openai_configured=health['openai_configured'],
            chroma_initialized=health['chroma_initialized']
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service unhealthy: {str(e)}"
        )


@router.post("/crawl", response_model=CrawlResponse, tags=["Crawling"])
async def crawl_website(request: CrawlRequest):
    """
    Crawl a website and index its content into the vector database.
    
    Args:
        request: CrawlRequest with URL and max_pages
        
    Returns:
        CrawlResponse with crawl statistics
    """
    try:
        logger.info(f"Received crawl request for: {request.url}")
        
        result = rag_service.crawl_and_index(
            url=str(request.url),
            max_pages=request.max_pages
        )
        
        return CrawlResponse(
            status="success",
            message=f"Successfully crawled and indexed {result['pages_crawled']} pages",
            pages_crawled=result['pages_crawled'],
            pages_indexed=result['pages_indexed'],
            website_url=result['website_url']
        )
    
    except ValueError as e:
        logger.error(f"Crawl validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Crawl error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to crawl website: {str(e)}"
        )


@router.post("/query", response_model=QueryResponse, tags=["Query"])
async def query_rag(request: QueryRequest):
    """
    Query the RAG system with a question.
    
    Args:
        request: QueryRequest with question and top_k
        
    Returns:
        QueryResponse with answer and sources
    """
    try:
        logger.info(f"Received query: {request.question}")
        
        result = rag_service.query(
            question=request.question,
            top_k=request.top_k
        )
        
        return QueryResponse(
            answer=result['answer'],
            sources=result['sources'],
            question=request.question,
            model_used=result['model_used']
        )
    
    except ValueError as e:
        logger.error(f"Query validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Query error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process query: {str(e)}"
        )


@router.get("/stats", response_model=StatsResponse, tags=["Statistics"])
async def get_stats():
    """
    Get statistics about the indexed data.
    
    Returns:
        StatsResponse with database statistics
    """
    try:
        stats = rag_service.get_stats()
        
        return StatsResponse(
            total_documents=stats['total_chunks'],
            total_chunks=stats['total_chunks'],
            indexed_websites=stats['indexed_websites'],
            database_size_mb=stats['database_size_mb'],
            last_indexed=stats['last_indexed']
        )
    except Exception as e:
        logger.error(f"Stats error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get statistics: {str(e)}"
        )


@router.post("/reindex", response_model=ReindexResponse, tags=["Maintenance"])
async def reindex_data(request: ReindexRequest):
    """
    Reindex the database (optionally clearing existing data).
    
    Args:
        request: ReindexRequest with clear_existing flag
        
    Returns:
        ReindexResponse with reindex results
    """
    try:
        logger.info(f"Reindex request - Clear existing: {request.clear_existing}")
        
        chunks_count = rag_service.reindex(clear_existing=request.clear_existing)
        
        if request.clear_existing:
            message = "Database cleared successfully"
        else:
            message = f"Database contains {chunks_count} chunks"
        
        return ReindexResponse(
            status="success",
            message=message,
            chunks_reindexed=chunks_count
        )
    except Exception as e:
        logger.error(f"Reindex error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reindex: {str(e)}"
        )


@router.post("/clear", tags=["Maintenance"])
async def clear_database():
    """
    Clear all data from the vector database.
    
    Returns:
        Success message
    """
    try:
        logger.info("Clearing database")
        rag_service.clear_database()
        
        return {
            "status": "success",
            "message": "Database cleared successfully",
            "timestamp": datetime.now()
        }
    except Exception as e:
        logger.error(f"Clear database error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear database: {str(e)}"
        )
