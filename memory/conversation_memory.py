
from .base import VectorMemory
import time

class ConversationMemory(VectorMemory):
    """Memory specialized for conversation history"""
    
    def apply_decay(self, memory_id: str, decay_rate: float = 0.01) -> bool:
        """Apply time-based decay to a memory's relevance score"""
        metadata = self.metadata_store.get(memory_id)
        if not metadata:
            return False
            
        time_elapsed = (time.time() - metadata.get("timestamp", 0)) / (60 * 60 * 24)  # days
        
        current_score = metadata.get("relevance_score", 1.0)
        new_score = current_score * ((1 - decay_rate) ** time_elapsed)
        
        metadata["relevance_score"] = new_score
        self.metadata_store.set(memory_id, metadata)
        return True
    
    def apply_decay_to_all(self, user_id: str, decay_rate: float = 0.01) -> int:
        """Apply decay to all memories for a user"""
        memories = self.metadata_store.query({"user_id": user_id})
        updated = 0
        
        for memory_id in memories:
            if self.apply_decay(memory_id, decay_rate):
                updated += 1
                
        return updated
    
    def reinforce(self, memory_id: str, amount: float = 0.1) -> bool:
        """Reinforce a memory by increasing its relevance score"""
        metadata = self.metadata_store.get(memory_id)
        if not metadata:
            return False
            
        current_score = metadata.get("relevance_score", 1.0)
        metadata["relevance_score"] = min(1.0, current_score + amount)
        metadata["access_count"] = metadata.get("access_count", 0) + 1
        metadata["last_accessed"] = time.time()
        
        self.metadata_store.set(memory_id, metadata)
        return True
