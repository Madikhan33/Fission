"""
Thread-Safe Singleton Embedding Service
Loads BAAI/bge-m3 model once and provides dense/sparse vector generation
"""

from threading import Lock
from typing import Dict, Tuple, List
import numpy as np
from FlagEmbedding import BGEM3FlagModel


class SingletonMeta(type):
    """
    Thread-safe singleton metaclass implementation
    Ensures only one instance of the class is created
    """
    _instances = {}
    _lock: Lock = Lock()
    
    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
            return cls._instances[cls]


class EmbeddingService(metaclass=SingletonMeta):
    """
    Singleton service for generating embeddings using BAAI/bge-m3 model.
    Model is loaded once and shared across all requests.
    """
    
    def __init__(self):
        """Initialize the model only once"""
        if not hasattr(self, 'model'):
            print("🚀 Loading BAAI/bge-m3 model...")
            self.model = BGEM3FlagModel(
                'BAAI/bge-m3',
                use_fp16=True  # Use half precision for faster inference
            )
            print("✅ Model loaded successfully!")
            
            # Warmup: run a dummy inference to initialize CUDA/model
            self._warmup()
    
    def _warmup(self):
        """Warmup the model with a dummy sentence"""
        try:
            print("🔥 Warming up model...")
            dummy_text = "This is a warmup sentence for the embedding model."
            _ = self.model.encode(
                [dummy_text],
                return_dense=True,
                return_sparse=True
            )
            print("✅ Model warmup complete!")
        except Exception as e:
            print(f"⚠️ Warmup failed (non-critical): {e}")
    
    def encode_dense(self, text: str) -> np.ndarray:
        """
        Generate dense vector embeddings (1024 dimensions)
        
        Args:
            text: Input text to encode
            
        Returns:
            Dense vector of shape (1024,)
        """
        result = self.model.encode(
            [text],
            return_dense=True,
            return_sparse=False
        )
        return result['dense_vecs'][0]
    
    def encode_sparse(self, text: str) -> Dict:
        """
        Generate sparse vector embeddings
        
        Args:
            text: Input text to encode
            
        Returns:
            Dictionary with sparse vector representation
        """
        result = self.model.encode(
            [text],
            return_dense=False,
            return_sparse=True
        )
        return result['lexical_weights'][0]
    
    def encode_hybrid(self, text: str) -> Tuple[np.ndarray, Dict]:
        """
        Generate both dense and sparse embeddings simultaneously
        
        Args:
            text: Input text to encode
            
        Returns:
            Tuple of (dense_vector, sparse_vector)
        """
        result = self.model.encode(
            [text],
            return_dense=True,
            return_sparse=True
        )
        dense = result['dense_vecs'][0]
        sparse = result['lexical_weights'][0]
        return dense, sparse
    
    def encode_batch_hybrid(self, texts: List[str]) -> Tuple[np.ndarray, List[Dict]]:
        """
        Generate embeddings for multiple texts in batch
        
        Args:
            texts: List of texts to encode
            
        Returns:
            Tuple of (dense_vectors, sparse_vectors)
        """
        result = self.model.encode(
            texts,
            return_dense=True,
            return_sparse=True
        )
        return result['dense_vecs'], result['lexical_weights']
