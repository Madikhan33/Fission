"""
Smart Chunking Service
Uses RecursiveCharacterTextSplitter for intelligent text segmentation
"""

from typing import List, Dict
from langchain_text_splitters import RecursiveCharacterTextSplitter


class ChunkingService:
    """
    Service for splitting text into intelligent chunks
    Prioritizes splitting by paragraphs, then sentences, then words
    """
    
    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        separators: List[str] = None
    ):
        """
        Initialize the chunking service
        
        Args:
            chunk_size: Maximum characters per chunk
            chunk_overlap: Number of characters to overlap between chunks
            separators: Custom separators (default: paragraph -> sentence -> word)
        """
        if separators is None:
            # Smart separators: try to split by paragraphs first, then sentences
            separators = [
                "\n\n",  # Paragraphs
                "\n",    # Lines
                ". ",    # Sentences
                " ",     # Words
                ""       # Characters (fallback)
            ]
        
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=separators,
            length_function=len,
            is_separator_regex=False
        )
    
    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into chunks
        
        Args:
            text: Input text to chunk
            
        Returns:
            List of text chunks
        """
        if not text or not text.strip():
            return []
        
        chunks = self.splitter.split_text(text)
        # Filter out empty chunks
        return [chunk.strip() for chunk in chunks if chunk.strip()]
    
    def chunk_with_metadata(
        self,
        text: str,
        document_id: str,
        metadata: Dict = None
    ) -> List[Dict]:
        """
        Split text into chunks with metadata
        
        Args:
            text: Input text to chunk
            document_id: Unique identifier for the document
            metadata: Additional metadata to attach to each chunk
            
        Returns:
            List of dictionaries containing chunk text, document_id, and metadata
        """
        chunks = self.chunk_text(text)
        
        result = []
        for idx, chunk in enumerate(chunks):
            chunk_data = {
                "text": chunk,
                "document_id": document_id,
                "chunk_index": idx,
                "total_chunks": len(chunks)
            }
            
            # Add any additional metadata
            if metadata:
                chunk_data["metadata"] = metadata
            
            result.append(chunk_data)
        
        return result
