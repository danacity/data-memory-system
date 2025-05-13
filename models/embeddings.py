
from abc import ABC, abstractmethod
from typing import List, Union, Dict, Any
import numpy as np

class EmbeddingModel(ABC):
    """Abstract base class for embedding models"""
    
    @abstractmethod
    def encode(self, text: Union[str, List[str]]) -> np.ndarray:
        """Encode text into embedding vectors"""
        pass
    
    @abstractmethod
    def similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """Calculate similarity between two embeddings"""
        pass

class SentenceTransformerEmbedding(EmbeddingModel):
    """Wrapper for Sentence Transformers embedding models"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize with a model name"""
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(model_name)
    
    def encode(self, text: Union[str, List[str]]) -> np.ndarray:
        """Encode text into embedding vectors"""
        return self.model.encode(text)
    
    def similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """Calculate cosine similarity between two embeddings"""
        # Normalize the embeddings
        embedding1_normalized = embedding1 / np.linalg.norm(embedding1)
        embedding2_normalized = embedding2 / np.linalg.norm(embedding2)
        
        # Calculate cosine similarity
        return float(np.dot(embedding1_normalized, embedding2_normalized))

def get_embedding_model(config: Dict[str, Any] = None) -> EmbeddingModel:
    """Factory function to get an embedding model based on configuration"""
    if config is None:
        config = {"provider": "sentence-transformers", "model_name": "all-MiniLM-L6-v2"}
    
    provider = config.get("provider", "sentence-transformers").lower()
    
    if provider == "sentence-transformers":
        model_name = config.get("model_name", "all-MiniLM-L6-v2")
        return SentenceTransformerEmbedding(model_name)
    else:
        raise ValueError(f"Unsupported embedding provider: {provider}")
