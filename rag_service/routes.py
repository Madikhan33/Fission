"""
FastAPI Routes for RAG Microservice
Provides endpoints for document management and search
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional, Dict

from orchestrator import RAGOrchestrator


# Pydantic models for request/response
class DocumentRequest(BaseModel):
    """Request model for indexing a document"""
    text: str = Field(..., description="Text content to index")
    document_id: str = Field(..., description="Unique document identifier")
    metadata: Optional[Dict] = Field(None, description="Optional metadata")


class SearchRequest(BaseModel):
    """Request model for search"""
    query: str = Field(..., description="Search query text")
    top_k: int = Field(5, ge=1, le=100, description="Number of results")
    search_type: str = Field("hybrid", description="Search type: hybrid, dense, or sparse")
    dense_weight: float = Field(0.5, ge=0.0, le=1.0, description="Weight for dense search")
    sparse_weight: float = Field(0.5, ge=0.0, le=1.0, description="Weight for sparse search")


class DocumentResponse(BaseModel):
    """Response model for document operations"""
    status: str
    document_id: str
    message: str
    chunk_count: Optional[int] = None


class SearchResult(BaseModel):
    """Single search result"""
    text: str
    document_id: str
    score: float
    id: Optional[int] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    model_loaded: bool
    milvus_connected: bool
    collection_stats: Optional[Dict] = None


# Initialize router
router = APIRouter()

# Initialize RAG orchestrator (singleton-like, created once)
rag_orchestrator: Optional[RAGOrchestrator] = None


def get_orchestrator() -> RAGOrchestrator:
    """Get or create RAG orchestrator instance"""
    global rag_orchestrator
    if rag_orchestrator is None:
        rag_orchestrator = RAGOrchestrator()
    return rag_orchestrator


@router.post("/documents", response_model=DocumentResponse)
async def index_document(request: DocumentRequest):
    """
    Index a text document in the RAG system
    
    This endpoint:
    1. Chunks the text into segments
    2. Generates embeddings (dense + sparse)
    3. Stores in Milvus vector database
    """
    try:
        orchestrator = get_orchestrator()
        
        result = orchestrator.process_text(
            text=request.text,
            document_id=request.document_id,
            metadata=request.metadata
        )
        
        if result["status"] == "error":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["message"]
            )
        
        return DocumentResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to index document: {str(e)}"
        )


@router.post("/search", response_model=List[SearchResult])
async def search_documents(request: SearchRequest):
    """
    Search for relevant documents using hybrid search
    
    Supports three search types:
    - hybrid: Combines dense and sparse search with RRF
    - dense: Semantic vector search only
    - sparse: Keyword-based search only
    """
    try:
        orchestrator = get_orchestrator()
        
        results = orchestrator.search(
            query=request.query,
            top_k=request.top_k,
            search_type=request.search_type,
            dense_weight=request.dense_weight,
            sparse_weight=request.sparse_weight
        )
        
        return [SearchResult(**result) for result in results]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )


@router.get("/documents/{document_id}")
async def get_document(document_id: str):
    """
    Retrieve all chunks for a specific document
    """
    try:
        orchestrator = get_orchestrator()
        chunks = orchestrator.get_document_chunks(document_id)
        
        if not chunks:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document {document_id} not found"
            )
        
        return {
            "document_id": document_id,
            "chunk_count": len(chunks),
            "chunks": chunks
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve document: {str(e)}"
        )


@router.delete("/documents/{document_id}", response_model=DocumentResponse)
async def delete_document(document_id: str):
    """
    Delete all chunks belonging to a document
    """
    try:
        orchestrator = get_orchestrator()
        result = orchestrator.delete_document(document_id)
        
        if result["status"] == "error":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["message"]
            )
        
        return DocumentResponse(**result, chunk_count=None)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete document: {str(e)}"
        )


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Check RAG service health status
    
    Returns:
    - Model loading status
    - Milvus connection status
    - Collection statistics
    """
    try:
        orchestrator = get_orchestrator()
        stats = orchestrator.get_stats()
        
        return HealthResponse(
            status=stats["status"],
            model_loaded=stats.get("model_loaded", False),
            milvus_connected=stats["status"] == "healthy",
            collection_stats=stats.get("collection")
        )
        
    except Exception as e:
        return HealthResponse(
            status="unhealthy",
            model_loaded=False,
            milvus_connected=False,
            collection_stats={"error": str(e)}
        )
