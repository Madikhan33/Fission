"""
RAG Orchestrator Service
Coordinates the entire RAG pipeline: chunking -> embedding -> storage -> search
"""

from typing import List, Dict, Optional
import numpy as np

from embedding_service import EmbeddingService
from chunking_service import ChunkingService
from milvus_service import MilvusService


class RAGOrchestrator:
    """
    Orchestrates the complete RAG workflow
    Coordinates between chunking, embedding, and vector storage services
    """
    
    def __init__(
        self,
        milvus_host: str = "localhost",
        milvus_port: int = 19530,
        chunk_size: int = 500,
        chunk_overlap: int = 50
    ):
        """
        Initialize RAG orchestrator with all required services
        
        Args:
            milvus_host: Milvus server host
            milvus_port: Milvus server port
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
        """
        # Initialize services
        self.embedding_service = EmbeddingService()
        self.chunking_service = ChunkingService(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        self.milvus_service = MilvusService(
            host=milvus_host,
            port=milvus_port
        )
        
        # Ensure collection exists
        self.milvus_service.create_collection(drop_existing=False)
    
    def process_text(
        self,
        text: str,
        document_id: str,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Process text through the complete RAG pipeline
        
        Pipeline:
        1. Chunk text into segments
        2. Generate embeddings (dense + sparse) for each chunk
        3. Store in Milvus
        
        Args:
            text: Input text to process
            document_id: Unique identifier for this document
            metadata: Optional metadata to attach
            
        Returns:
            Processing result with statistics
        """
        try:
            # Step 1: Chunk text
            chunks_data = self.chunking_service.chunk_with_metadata(
                text=text,
                document_id=document_id,
                metadata=metadata
            )
            
            if not chunks_data:
                return {
                    "status": "error",
                    "message": "No chunks generated from text",
                    "document_id": document_id,
                    "chunk_count": 0
                }
            
            # Step 2: Generate embeddings
            texts = [chunk["text"] for chunk in chunks_data]
            dense_vecs, sparse_vecs = self.embedding_service.encode_batch_hybrid(texts)
            
            # Step 3: Prepare data for Milvus
            milvus_chunks = []
            for i, chunk in enumerate(chunks_data):
                milvus_chunks.append({
                    "document_id": chunk["document_id"],
                    "text": chunk["text"],
                    "dense_vector": dense_vecs[i].tolist(),
                    "sparse_vector": self.milvus_service.convert_sparse_to_milvus_format(
                        sparse_vecs[i]
                    )
                })
            
            # Step 4: Insert into Milvus
            self.milvus_service.insert_documents(milvus_chunks)
            
            return {
                "status": "success",
                "document_id": document_id,
                "chunk_count": len(chunks_data),
                "message": f"Successfully processed {len(chunks_data)} chunks"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "document_id": document_id,
                "message": f"Processing failed: {str(e)}"
            }
    
    def search(
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
            query: Search query text
            top_k: Number of results to return
            search_type: "hybrid", "dense", or "sparse"
            dense_weight: Weight for dense search (hybrid only)
            sparse_weight: Weight for sparse search (hybrid only)
            
        Returns:
            List of search results with scores
        """
        try:
            # Generate query embeddings
            if search_type in ["hybrid", "dense"]:
                query_dense = self.embedding_service.encode_dense(query)
            
            if search_type in ["hybrid", "sparse"]:
                query_sparse = self.embedding_service.encode_sparse(query)
            
            # Perform search based on type
            if search_type == "dense":
                results = self.milvus_service.dense_search(
                    query_vector=query_dense,
                    top_k=top_k
                )
            elif search_type == "sparse":
                results = self.milvus_service.sparse_search(
                    query_sparse=query_sparse,
                    top_k=top_k
                )
            elif search_type == "hybrid":
                results = self.milvus_service.hybrid_search(
                    query_dense=query_dense,
                    query_sparse=query_sparse,
                    top_k=top_k,
                    dense_weight=dense_weight,
                    sparse_weight=sparse_weight
                )
            else:
                raise ValueError(f"Invalid search_type: {search_type}")
            
            return results
            
        except Exception as e:
            print(f"❌ Search failed: {e}")
            return []
    
    def get_document_chunks(self, document_id: str) -> List[Dict]:
        """
        Retrieve all chunks for a specific document
        
        Args:
            document_id: Document ID to retrieve
            
        Returns:
            List of chunks belonging to the document
        """
        try:
            # Use dense search with document filter
            # We need to provide a dummy query vector
            dummy_vector = np.zeros(1024)
            results = self.milvus_service.dense_search(
                query_vector=dummy_vector,
                top_k=1000,  # Get all chunks
                document_id_filter=document_id
            )
            return results
        except Exception as e:
            print(f"❌ Failed to get document chunks: {e}")
            return []
    
    def delete_document(self, document_id: str) -> Dict:
        """
        Delete all chunks belonging to a document
        
        Args:
            document_id: Document ID to delete
            
        Returns:
            Deletion result
        """
        try:
            success = self.milvus_service.delete_by_document_id(document_id)
            
            if success:
                return {
                    "status": "success",
                    "document_id": document_id,
                    "message": f"Document {document_id} deleted successfully"
                }
            else:
                return {
                    "status": "error",
                    "document_id": document_id,
                    "message": "Deletion failed"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "document_id": document_id,
                "message": f"Deletion failed: {str(e)}"
            }
    
    def get_stats(self) -> Dict:
        """
        Get RAG system statistics
        
        Returns:
            System statistics
        """
        try:
            collection_stats = self.milvus_service.get_collection_stats()
            return {
                "status": "healthy",
                "model_loaded": True,
                "collection": collection_stats
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
