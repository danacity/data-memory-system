
from typing import Dict, Any

# LLM provider configuration
LLM_PROVIDER = "ollama"  # Options: openai, anthropic, ollama, etc.

# OpenAI configuration
OPENAI_CONFIG = {
    "provider": "openai",
    "api_key": "your-api-key-here",  # Should be loaded from environment variables
    "default_model": "gpt-4",
    "temperature": 0.2,
    "max_tokens": 1000
}

# Anthropic configuration
ANTHROPIC_CONFIG = {
    "provider": "anthropic",
    "api_key": "your-api-key-here",  # Should be loaded from environment variables
    "default_model": "claude-2",
    "temperature": 0.2,
    "max_tokens": 1000
}

# Ollama configuration
OLLAMA_CONFIG = {
    "provider": "ollama",
    "default_model": "gemma3:4b-it-qat",
    "temperature": 0.7
}

# Get the active LLM configuration
def get_active_llm_config() -> Dict[str, Any]:
    """Get the active LLM configuration based on LLM_PROVIDER"""
    if LLM_PROVIDER == "openai":
        return OPENAI_CONFIG
    elif LLM_PROVIDER == "anthropic":
        return ANTHROPIC_CONFIG
    elif LLM_PROVIDER == "ollama":
        return OLLAMA_CONFIG
    else:
        raise ValueError(f"Unsupported LLM provider: {LLM_PROVIDER}")

# Embedding model configuration
EMBEDDING_CONFIG = {
    "provider": "sentence-transformers",
    "model_name": "all-MiniLM-L6-v2"
}
