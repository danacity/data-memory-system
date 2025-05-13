
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional

class BaseMemory(ABC):
    """Abstract base class for memory implementations"""
    
    @abstractmethod
    def store(self, content: Any, user_id: str, **metadata) -> str:
        """Store a memory and return its ID"""
        pass
    
    @abstractmethod
    def retrieve(self, query: Any, user_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Retrieve memories similar to the query"""
        pass
    
    @abstractmethod
    def update(self, memory_id: str, **updates) -> bool:
        """Update a memory with new information"""
        pass
    
    @abstractmethod
    def delete(self, memory_id: str) -> bool:
        """Delete a memory"""
        pass

class VectorMemory(BaseMemory):
    """Base implementation of vector-based memory"""
    
    def __init__(self, embedding_model, vector_store, metadata_store):
        self.embedding_model = embedding_model
        self.vector_store = vector_store
        self.metadata_store = metadata_store
        
    def store(self, content: str, user_id: str, **metadata) -> str:
        """Store content with vector embeddings and metadata"""
        # Generate embedding
        embedding = self.embedding_model.encode(content)
        
        # Create memory ID
        import time
        memory_id = f"{user_id}_{time.time()}"
        
        # Store vector
        self.vector_store.add(memory_id, embedding)
        
        # Store metadata
        self.metadata_store.set(memory_id, {
            "content": content,
            "user_id": user_id,
            "timestamp": time.time(),
            **metadata
        })
        
        return memory_id
    
    def retrieve(self, query: str, user_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Retrieve similar memories based on vector similarity"""
        # Generate query embedding
        query_embedding = self.embedding_model.encode(query)
        
        # Search vector store
        results = self.vector_store.search(query_embedding, limit=limit, filter={"user_id": user_id})
        
        # Fetch metadata
        memories = []
        for memory_id, score in results:
            metadata = self.metadata_store.get(memory_id)
            if metadata:
                memories.append({
                    "memory_id": memory_id,
                    "content": metadata.get("content", ""),
                    "relevance": score,
                    **metadata
                })
                
        return memories
    
    def update(self, memory_id: str, **updates) -> bool:
        """Update memory metadata"""
        metadata = self.metadata_store.get(memory_id)
        if not metadata:
            return False
            
        # Update metadata
        metadata.update(updates)
        self.metadata_store.set(memory_id, metadata)
        
        # If content changed, update vector
        if "content" in updates:
            embedding = self.embedding_model.encode(updates["content"])
            self.vector_store.update(memory_id, embedding)
            
        return True
    
    def delete(self, memory_id: str) -> bool:
        """Delete a memory"""
        self.metadata_store.delete(memory_id)
        self.vector_store.delete(memory_id)
        return True
