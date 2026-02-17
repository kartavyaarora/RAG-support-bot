#!/usr/bin/env python3
"""
Run script for RAG Q&A Support Bot
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    import uvicorn
    from app.config import settings
    
    print("=" * 60)
    print("Starting RAG Q&A Support Bot API Server")
    print("=" * 60)
    print(f"Server will be available at: http://{settings.app_host}:{settings.app_port}")
    print(f"API Documentation: http://{settings.app_host}:{settings.app_port}/docs")
    print(f"ReDoc Documentation: http://{settings.app_host}:{settings.app_port}/redoc")
    print("=" * 60)
    print("\nPress CTRL+C to stop the server\n")
    
    uvicorn.run(
        "app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=True,
        log_level=settings.log_level
    )
