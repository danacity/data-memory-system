
import sqlite3
from typing import Dict, Any, List, Optional

class SQLiteStore:
    """Simple SQLite-based metadata store"""
    
    def __init__(self, db_path: str = "memory.db"):
        self.db_path = db_path
        self._initialize_db()
    
    def _initialize_db(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create metadata table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS metadata (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            content TEXT,
            metadata TEXT,
            timestamp REAL
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def set(self, key: str, value: Dict[str, Any]) -> bool:
        """Set a key-value pair"""
        import json
        
        # Extract common fields
        user_id = value.get("user_id", "")
        content = value.get("content", "")
        timestamp = value.get("timestamp", 0.0)
        
        # Convert remaining metadata to JSON
        metadata_json = json.dumps({k: v for k, v in value.items()
                                   if k not in ["user_id", "content"]})
        
        # Insert or replace
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT OR REPLACE INTO metadata (id, user_id, content, metadata, timestamp) VALUES (?, ?, ?, ?, ?)",
            (key, user_id, content, metadata_json, timestamp)
        )
        
        conn.commit()
        conn.close()
        
        return True
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get a value by key"""
        import json
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT user_id, content, metadata, timestamp FROM metadata WHERE id = ?", (key,))
        row = cursor.fetchone()
        
        conn.close()
        
        if not row:
            return None
            
        user_id, content, metadata_json, timestamp = row
        
        # Parse metadata
        metadata = json.loads(metadata_json)
        
        # Combine all fields
        return {
            "user_id": user_id,
            "content": content,
            "timestamp": timestamp,
            **metadata
        }
    
    def delete(self, key: str) -> bool:
        """Delete a key-value pair"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM metadata WHERE id = ?", (key,))
        
        deleted = cursor.rowcount > 0
        
        conn.commit()
        conn.close()
        
        return deleted
    
    def query(self, filters: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Query keys matching filters"""
        import json
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Build query conditions
        conditions = []
        params = []
        
        if "user_id" in filters:
            conditions.append("user_id = ?")
            params.append(filters["user_id"])
            
        # To search in metadata, we'd need a more complex approach
        # This is a simplified version
        
        query = f"SELECT id, user_id, content, metadata, timestamp FROM metadata"
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
            
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        conn.close()
        
        results = {}
        for id, user_id, content, metadata_json, timestamp in rows:
            metadata = json.loads(metadata_json)
            
            # Check if metadata matches filters
            skip = False
            for key, value in filters.items():
                if key != "user_id" and (key not in metadata or metadata[key] != value):
                    skip = True
                    break
                    
            if skip:
                continue
                
            results[id] = {
                "user_id": user_id,
                "content": content,
                "timestamp": timestamp,
                **metadata
            }
            
        return results
