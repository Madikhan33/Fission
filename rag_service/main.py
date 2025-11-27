"""
RAG Microservice - Main Application
Standalone FastAPI service for hybrid RAG search
"""

from fastapi import FastAPI
from contextlib import asynccontextmanager

from embedding_service import EmbeddingService
from routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler
    Loads the embedding model on startup and keeps it in memory
    """
    # Startup: Load embedding model ONCE
    print("=" * 60)
    print("🚀 RAG Microservice Starting...")
    print("=" * 60)
    
    # Initialize embedding service (singleton - loads model once)
    embedding_service = EmbeddingService()
    
    print("=" * 60)
    print("✅ RAG Microservice Ready!")
    print("   - Model: BAAI/bge-m3")
    print("   - Port: 8001")
    print("   - Endpoints: /api/rag/...")
    print("=" * 60)
    
    yield
    
    # Shutdown
    print("🔻 RAG Microservice shutting down...")


# Create FastAPI app
app = FastAPI(
    title="RAG Microservice",
    description="Hybrid search RAG system with BAAI/bge-m3 embeddings",
    version="1.0.0",
    lifespan=lifespan
)

# Include routes
app.include_router(router, prefix="/api/rag", tags=["RAG"])


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "service": "RAG Microservice",
        "version": "1.0.0",
        "status": "healthy",
        "docs": "/docs"
    }


@app.get("/health")
def health():
    """Simple health check"""
    return {
        "status": "healthy",
        "service": "rag-microservice"
    }


if __name__ == "__main__":
    from granian import Granian
    
    # Run the service using Granian
    # reload=False ensures model stays loaded during development
    server = Granian(
        "main:app",
        address="0.0.0.0",
        port=8001,
        interface="asgi",
        reload=False,  # IMPORTANT: No reload to keep model in memory
        log_level="info"
    )
    server.serve()
