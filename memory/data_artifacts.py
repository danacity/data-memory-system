
import json
import hashlib
import time
from .base import VectorMemory

class DataArtifactMemory(VectorMemory):
    """Memory specialized for data artifacts like tables and visualizations"""
    
    def store(self, data_content: Any, user_id: str, **metadata) -> str:
        """Store a data artifact"""
        # Convert to string if needed
        if not isinstance(data_content, str):
            data_content = json.dumps(data_content)
            
        # Generate hash for deduplication
        content_hash = hashlib.md5(data_content.encode()).hexdigest()
        
        # Check if duplicate exists
        existing = self.metadata_store.query({
            "user_id": user_id,
            "content_hash": content_hash
        })
        
        if existing:
            # Return existing artifact ID
            return list(existing.keys())[0]
            
        # Create summary if not provided
        if "summary" not in metadata:
            metadata["summary"] = self._generate_summary(data_content, metadata.get("data_type", "unknown"))
            
        # Use summary for embedding, not raw data
        embedding_text = metadata.get("summary", "")
        embedding = self.embedding_model.encode(embedding_text)
        
        # Create memory ID
        memory_id = f"{user_id}_{time.time()}_artifact"
        
        # Store vector
        self.vector_store.add(memory_id, embedding)
        
        # Store metadata and content
        self.metadata_store.set(memory_id, {
            "content": data_content,
            "user_id": user_id,
            "timestamp": time.time(),
            "content_hash": content_hash,
            **metadata
        })
        
        return memory_id
    
    def _generate_summary(self, data_content: str, data_type: str) -> str:
        """Generate a summary of data content"""
        try:
            if data_type == "table":
                data = json.loads(data_content)
                if isinstance(data, list) and data:
                    return f"Table with {len(data)} rows and {len(data[0])} columns"
            elif data_type == "network_diagram":
                data = json.loads(data_content)
                nodes = len(data.get("nodes", []))
                edges = len(data.get("edges", []))
                return f"Network diagram with {nodes} nodes and {edges} connections"
        except:
            pass
            
        return f"Data artifact of type {data_type}"
    
    def get_preview(self, memory_id: str, max_rows: int = 5) -> str:
        """Get a text preview of a data artifact"""
        metadata = self.metadata_store.get(memory_id)
        if not metadata:
            return "Data preview unavailable"
            
        data_type = metadata.get("data_type", "unknown")
        data_content = metadata.get("content", "{}")
        
        try:
            if data_type == "table":
                data = json.loads(data_content)
                if isinstance(data, list) and data:
                    preview = f"Table preview ({min(len(data), max_rows)} of {len(data)} rows):\n"
                    for i, row in enumerate(data[:max_rows]):
                        preview += f"Row {i+1}: {json.dumps(row)[:100]}...\n"
                    return preview
        except:
            pass
            
        return f"Preview for {data_type} not available"
