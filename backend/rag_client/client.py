"""
HTTP Client for RAG Microservice
Provides async methods to interact with the RAG service
"""

import httpx
from typing import List, Dict, Optional


class RAGClient:
    """
    Async HTTP client for RAG microservice
    Handles communication between main backend and RAG service
    """
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        """
        Initialize RAG client
        
        Args:
            base_url: Base URL of the RAG microservice
        """
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def index_document(
        self,
        text: str,
        document_id: str,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Index a document in the RAG system
        
        Args:
            text: Document text to index
            document_id: Unique document identifier
            metadata: Optional metadata
            
        Returns:
            Indexing result with status and chunk count
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/api/rag/documents",
                json={
                    "text": text,
                    "document_id": document_id,
                    "metadata": metadata
                }
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            return {
                "status": "error",
                "message": f"Failed to index document: {str(e)}"
            }
    
    async def search(
        self,
        query: str,
        top_k: int = 5,
        search_type: str = "hybrid",
        dense_weight: float = 0.5,
        sparse_weight: float = 0.5
    ) -> List[Dict]:
        """
        Search for relevant documents
        
        Args:
            query: Search query
            top_k: Number of results to return
            search_type: "hybrid", "dense", or "sparse"
            dense_weight: Weight for dense search (hybrid only)
            sparse_weight: Weight for sparse search (hybrid only)
            
        Returns:
            List of search results with scores
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/api/rag/search",
                json={
                    "query": query,
                    "top_k": top_k,
                    "search_type": search_type,
                    "dense_weight": dense_weight,
                    "sparse_weight": sparse_weight
                }
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            print(f"Search error: {e}")
            return []
    
    async def get_document(self, document_id: str) -> Optional[Dict]:
        """
        Retrieve a document and its chunks
        
        Args:
            document_id: Document ID to retrieve
            
        Returns:
            Document data with chunks or None if not found
        """
        try:
            response = await self.client.get(
                f"{self.base_url}/api/rag/documents/{document_id}"
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            print(f"Error retrieving document: {e}")
            return None
        except httpx.HTTPError as e:
            print(f"Error retrieving document: {e}")
            return None
    
    async def delete_document(self, document_id: str) -> Dict:
        """
        Delete a document from the RAG system
        
        Args:
            document_id: Document ID to delete
            
        Returns:
            Deletion result
        """
        try:
            response = await self.client.delete(
                f"{self.base_url}/api/rag/documents/{document_id}"
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            return {
                "status": "error",
                "message": f"Failed to delete document: {str(e)}"
            }
    
    async def health_check(self) -> Dict:
        """
        Check RAG service health
        
        Returns:
            Health status information
        """
        try:
            response = await self.client.get(
                f"{self.base_url}/api/rag/health"
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()


# Example usage in FastAPI endpoint:
"""
from rag_client import RAGClient

@app.post("/documents/analyze")
async def analyze_document(text: str, doc_id: str):
    rag_client = RAGClient()
    
    # Index the document
    result = await rag_client.index_document(text, doc_id)
    
    # Search for similar content
    results = await rag_client.search("your query", top_k=3)
    
    await rag_client.close()
    return {"indexing": result, "search": results}
"""
