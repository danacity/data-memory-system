
from typing import Dict, Any

# MCP server configuration
MCP_SERVERS = {
    "memory": {
        "script_path": "mcp_servers/memory_server.py",
        "port": 5000
    },
    "sql": {
        "script_path": "mcp_servers/sql_agent_server.py",
        "port": 5001
    },
    "visualization": {
        "script_path": "mcp_servers/data_visualization_server.py",
        "port": 5002
    },
    "summarization": {
        "script_path": "mcp_servers/data_summarization_server.py",
        "port": 5003
    }
}

# Database configuration
DATABASE_CONFIG = {
    "type": "sqlite",
    "path": "data/memory.db"
}

# Vector store configuration
VECTOR_STORE_CONFIG = {
    "type": "faiss",  # Options: faiss, pinecone, etc.
    "path": "data/vector_store"
}
