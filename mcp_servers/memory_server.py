from mcp.server.fastmcp import FastMCP
import numpy as np
import json
import time
import hashlib
from sentence_transformers import SentenceTransformer

# Initialize MCP server
mcp = FastMCP("memory_server")

# Initialize embedding model
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
embedding_dimension = 384

# In-memory storage for this example
# In production, would use proper databases
conversation_memories = {}
data_artifacts = {}
memory_embeddings = {}

@mcp.tool()
def store_memory(text: str, user_id: str, memory_type: str = "conversation") -> str:
    """Store a new memory in the memory bank"""
    # Generate embedding
    embedding = embedding_model.encode(text)
    
    # Create memory entry
    timestamp = time.time()
    memory_id = f"{user_id}_{timestamp}_{memory_type}"
    
    # Store memory
    conversation_memories[memory_id] = {
        "text": text,
        "user_id": user_id,
        "memory_type": memory_type,
        "timestamp": timestamp,
        "relevance_score": 1.0,
        "access_count": 0,
        "last_accessed": timestamp
    }
    
    # Store embedding
    memory_embeddings[memory_id] = embedding
    
    return memory_id

@mcp.tool()
def store_data_artifact(memory_id: str, data_type: str, data_content: str, summary: str) -> str:
    """Store a data artifact associated with a memory"""
    # Generate hash of content for deduplication
    content_hash = hashlib.md5(data_content.encode()).hexdigest()
    
    # Create artifact ID
    artifact_id = f"{memory_id}_{data_type}"
    
    # Store in database
    data_artifacts[artifact_id] = {
        "memory_id": memory_id,
        "data_type": data_type,
        "data_content": data_content,
        "summary": summary,
        "hash": content_hash,
        "timestamp": time.time()
    }
    
    # Also store embedding of summary for retrieval
    summary_embedding = embedding_model.encode(summary)
    memory_embeddings[artifact_id] = summary_embedding
    
    return artifact_id

@mcp.tool()
def retrieve_conversation_context(query: str, user_id: str, max_results: int = 5) -> str:
    """Retrieve relevant conversation memories for context"""
    # Generate query embedding
    query_embedding = embedding_model.encode(query)
    
    # Find relevant memories
    results = []
    for memory_id, embedding in memory_embeddings.items():
        # Check if it's a conversation memory for this user
        if memory_id in conversation_memories and conversation_memories[memory_id]["user_id"] == user_id:
            # Calculate similarity
            similarity = np.dot(query_embedding, embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(embedding)
            )
            
            memory = conversation_memories[memory_id]
            
            # Apply time decay
            time_elapsed = (time.time() - memory["timestamp"]) / (60 * 60 * 24)  # days
            decay_rate = 0.01
            decayed_score = memory["relevance_score"] * ((1 - decay_rate) ** time_elapsed)
            
            # Final score is combination of relevance and similarity
            final_score = (decayed_score + similarity) / 2
            
            if final_score >= 0.5:  # relevance threshold
                results.append({
                    "memory_id": memory_id,
                    "text": memory["text"],
                    "type": memory["memory_type"],
                    "relevance": float(final_score)
                })
    
    # Sort by relevance
    results.sort(key=lambda x: x["relevance"], reverse=True)
    
    # Return top results
    return json.dumps({"memories": results[:max_results]})

@mcp.tool()
def retrieve_data_artifacts(query: str, user_id: str, max_results: int = 3) -> str:
    """Retrieve relevant data artifacts based on query"""
    # Generate query embedding
    query_embedding = embedding_model.encode(query)
    
    # Find relevant artifacts
    results = []
    for artifact_id, embedding in memory_embeddings.items():
        # Check if it's a data artifact
        if artifact_id in data_artifacts:
            artifact = data_artifacts[artifact_id]
            memory_id = artifact["memory_id"]
            
            # Check if it belongs to this user
            if memory_id in conversation_memories and conversation_memories[memory_id]["user_id"] == user_id:
                # Calculate similarity
                similarity = np.dot(query_embedding, embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(embedding)
                )
                
                if similarity >= 0.5:  # relevance threshold
                    results.append({
                        "artifact_id": artifact_id,
                        "memory_id": memory_id,
                        "data_type": artifact["data_type"],
                        "summary": artifact["summary"],
                        "relevance": float(similarity),
                        "data_content": artifact["data_content"]
                    })
    
    # Sort by relevance
    results.sort(key=lambda x: x["relevance"], reverse=True)
    
    # Return top results
    return json.dumps({"artifacts": results[:max_results]})

@mcp.prompt()
def memory_system_prompt() -> str:
    """Memory system prompt"""
    return """
    This assistant has access to a memory system that stores:
    1. Conversation history
    2. Data artifacts (visualizations, query results)
    
    The assistant can retrieve relevant memories based on the current context.
    """

if __name__ == "__main__":
    mcp.run()