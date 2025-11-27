"""
Milvus Hybrid Search Service
Manages Milvus collection with dense and sparse vectors
"""

from typing import List, Dict, Optional
from pymilvus import (
    connections,
    Collection,
    CollectionSchema,
    FieldSchema,
    DataType,
    utility
)
import numpy as np


class MilvusService:
    """
    Service for managing Milvus vector database with hybrid search
    Supports both dense (HNSW) and sparse (Inverted Index) vector searches
    """
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 19530,
        collection_name: str = "rag_documents"
    ):
        """
        Initialize Milvus connection
        
        Args:
            host: Milvus server host
            port: Milvus server port
            collection_name: Name of the collection to use
        """
        self.host = host
        self.port = port
        self.collection_name = collection_name
        self.collection: Optional[Collection] = None
        
        # Connect to Milvus
        self._connect()
    
    def _connect(self):
        """Establish connection to Milvus"""
        try:
            connections.connect(
                alias="default",
                host=self.host,
                port=self.port
            )
            print(f"✅ Connected to Milvus at {self.host}:{self.port}")
        except Exception as e:
            print(f"❌ Failed to connect to Milvus: {e}")
            raise
    
    def create_collection(self, drop_existing: bool = False):
        """
        Create Milvus collection with schema for hybrid search
        
        Args:
            drop_existing: If True, drop existing collection before creating
        """
        # Drop existing collection if requested
        if drop_existing and utility.has_collection(self.collection_name):
            utility.drop_collection(self.collection_name)
            print(f"🗑️ Dropped existing collection: {self.collection_name}")
        
        # Check if collection already exists
        if utility.has_collection(self.collection_name):
            self.collection = Collection(self.collection_name)
            print(f"✅ Using existing collection: {self.collection_name}")
            return
        
        # Define schema
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="document_id", dtype=DataType.VARCHAR, max_length=255),
            FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="dense_vector", dtype=DataType.FLOAT_VECTOR, dim=1024),
            FieldSchema(name="sparse_vector", dtype=DataType.SPARSE_FLOAT_VECTOR)
        ]
        
        schema = CollectionSchema(
            fields=fields,
            description="RAG documents with hybrid search support"
        )
        
        # Create collection
        self.collection = Collection(
            name=self.collection_name,
            schema=schema
        )
        print(f"✅ Created collection: {self.collection_name}")
        
        # Create indexes
        self._create_indexes()
    
    def _create_indexes(self):
        """Create indexes for dense and sparse vectors"""
        # Dense vector index (HNSW)
        dense_index_params = {
            "index_type": "HNSW",
            "metric_type": "IP",  # Inner Product (cosine similarity for normalized vectors)
            "params": {
                "M": 16,
                "efConstruction": 200
            }
        }
        
        self.collection.create_index(
            field_name="dense_vector",
            index_params=dense_index_params
        )
        print("✅ Created HNSW index for dense vectors")
        
        # Sparse vector index (Inverted Index)
        sparse_index_params = {
            "index_type": "SPARSE_INVERTED_INDEX",
            "metric_type": "IP",
            "params": {
                "drop_ratio_build": 0.2
            }
        }
        
        self.collection.create_index(
            field_name="sparse_vector",
            index_params=sparse_index_params
        )
        print("✅ Created SPARSE_INVERTED_INDEX for sparse vectors")
        
        # Load collection into memory
        self.collection.load()
        print("✅ Collection loaded into memory")
    
    def insert_documents(self, chunks: List[Dict]):
        """
        Insert document chunks with embeddings
        
        Args:
            chunks: List of dicts with 'text', 'document_id', 'dense_vector', 'sparse_vector'
        """
        if not chunks:
            return
        
        # Prepare data for insertion
        data = [
            [chunk["document_id"] for chunk in chunks],
            [chunk["text"] for chunk in chunks],
            [chunk["dense_vector"] for chunk in chunks],
            [chunk["sparse_vector"] for chunk in chunks]
        ]
        
        # Insert
        self.collection.insert(data)
        self.collection.flush()
        print(f"✅ Inserted {len(chunks)} chunks into Milvus")
    
    def convert_sparse_to_milvus_format(self, sparse_dict: Dict) -> Dict:
        """
        Convert sparse vector from dict format to Milvus sparse format
        
        Args:
            sparse_dict: Dictionary with token indices as keys and weights as values
            
        Returns:
            Milvus-compatible sparse vector
        """
        # Milvus expects sparse vectors in {index: weight} format
        return sparse_dict
    
    def dense_search(
        self,
        query_vector: np.ndarray,
        top_k: int = 5,
        document_id_filter: Optional[str] = None
    ) -> List[Dict]:
        """
        Search using dense vectors only
        
        Args:
            query_vector: Dense query vector
            top_k: Number of results to return
            document_id_filter: Optional filter by document_id
            
        Returns:
            List of search results with scores
        """
        search_params = {
            "metric_type": "IP",
            "params": {"ef": 100}
        }
        
        expr = f'document_id == "{document_id_filter}"' if document_id_filter else None
        
        results = self.collection.search(
            data=[query_vector.tolist()],
            anns_field="dense_vector",
            param=search_params,
            limit=top_k,
            expr=expr,
            output_fields=["document_id", "text"]
        )
        
        return self._format_results(results[0])
    
    def sparse_search(
        self,
        query_sparse: Dict,
        top_k: int = 5,
        document_id_filter: Optional[str] = None
    ) -> List[Dict]:
        """
        Search using sparse vectors only
        
        Args:
            query_sparse: Sparse query vector
            top_k: Number of results to return
            document_id_filter: Optional filter by document_id
            
        Returns:
            List of search results with scores
        """
        search_params = {
            "metric_type": "IP",
            "params": {}
        }
        
        expr = f'document_id == "{document_id_filter}"' if document_id_filter else None
        
        results = self.collection.search(
            data=[query_sparse],
            anns_field="sparse_vector",
            param=search_params,
            limit=top_k,
            expr=expr,
            output_fields=["document_id", "text"]
        )
        
        return self._format_results(results[0])
    
    def hybrid_search(
        self,
        query_dense: np.ndarray,
        query_sparse: Dict,
        top_k: int = 5,
        dense_weight: float = 0.5,
        sparse_weight: float = 0.5
    ) -> List[Dict]:
        """
        Hybrid search using RRF (Reciprocal Rank Fusion)
        
        Args:
            query_dense: Dense query vector
            query_sparse: Sparse query vector
            top_k: Number of results to return
            dense_weight: Weight for dense search results
            sparse_weight: Weight for sparse search results
            
        Returns:
            List of search results ranked by RRF
        """
        # Get results from both searches (get more to ensure good fusion)
        k_multiplier = 3
        dense_results = self.dense_search(query_dense, top_k * k_multiplier)
        sparse_results = self.sparse_search(query_sparse, top_k * k_multiplier)
        
        # Apply RRF
        fused_results = self._reciprocal_rank_fusion(
            dense_results,
            sparse_results,
            dense_weight,
            sparse_weight,
            k=60
        )
        
        # Return top_k
        return fused_results[:top_k]
    
    def _reciprocal_rank_fusion(
        self,
        dense_results: List[Dict],
        sparse_results: List[Dict],
        dense_weight: float,
        sparse_weight: float,
        k: int = 60
    ) -> List[Dict]:
        """
        Combine results using Reciprocal Rank Fusion
        
        Args:
            dense_results: Results from dense search
            sparse_results: Results from sparse search
            dense_weight: Weight for dense results
            sparse_weight: Weight for sparse results
            k: RRF constant (usually 60)
            
        Returns:
            Fused and ranked results
        """
        # Create a mapping of document text to RRF score
        scores = {}
        
        # Process dense results
        for rank, result in enumerate(dense_results, 1):
            text = result["text"]
            rrf_score = dense_weight / (k + rank)
            if text not in scores:
                scores[text] = {"score": 0, "data": result}
            scores[text]["score"] += rrf_score
        
        # Process sparse results
        for rank, result in enumerate(sparse_results, 1):
            text = result["text"]
            rrf_score = sparse_weight / (k + rank)
            if text not in scores:
                scores[text] = {"score": 0, "data": result}
            scores[text]["score"] += rrf_score
        
        # Sort by RRF score
        sorted_results = sorted(
            scores.values(),
            key=lambda x: x["score"],
            reverse=True
        )
        
        # Format results
        return [
            {
                **item["data"],
                "rrf_score": item["score"]
            }
            for item in sorted_results
        ]
    
    def _format_results(self, results) -> List[Dict]:
        """Format Milvus search results"""
        formatted = []
        for hit in results:
            formatted.append({
                "id": hit.id,
                "document_id": hit.entity.get("document_id"),
                "text": hit.entity.get("text"),
                "score": hit.score
            })
        return formatted
    
    def delete_by_document_id(self, document_id: str) -> bool:
        """
        Delete all chunks belonging to a document
        
        Args:
            document_id: Document ID to delete
            
        Returns:
            True if successful
        """
        try:
            expr = f'document_id == "{document_id}"'
            self.collection.delete(expr)
            self.collection.flush()
            print(f"✅ Deleted document: {document_id}")
            return True
        except Exception as e:
            print(f"❌ Failed to delete document {document_id}: {e}")
            return False
    
    def get_collection_stats(self) -> Dict:
        """Get collection statistics"""
        return {
            "name": self.collection_name,
            "num_entities": self.collection.num_entities,
            "loaded": utility.load_state(self.collection_name)
        }
