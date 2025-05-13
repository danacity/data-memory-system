
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union

class LLMService(ABC):
    """Abstract base class for LLM services"""
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text from a prompt"""
        pass
    
    @abstractmethod
    def generate_with_tools(self, prompt: str, tools: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        """Generate text with potential tool calls"""
        pass

class OpenAIService(LLMService):
    """OpenAI API service"""
    
    def __init__(self, api_key: str, model: str = "gpt-4"):
        """Initialize with API key and model"""
        import openai
        openai.api_key = api_key
        self.model = model
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text from a prompt"""
        import openai
        
        # Set default parameters
        params = {
            "model": self.model,
            "max_tokens": 1000,
            "temperature": 0.2,
            **kwargs
        }
        
        # Call the API
        response = openai.ChatCompletion.create(
            model=params["model"],
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=params["max_tokens"],
            temperature=params["temperature"]
        )
        
        return response.choices[0].message.content
    
    def generate_with_tools(self, prompt: str, tools: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        """Generate text with potential tool calls"""
        import openai
        import json
        
        # Format tools for OpenAI API
        formatted_tools = [
            {
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool.get("description", ""),
                    "parameters": tool.get("parameters", {})
                }
            }
            for tool in tools
        ]
        
        # Set default parameters
        params = {
            "model": self.model,
            "max_tokens": 1000,
            "temperature": 0.2,
            **kwargs
        }
        
        # Call the API
        response = openai.ChatCompletion.create(
            model=params["model"],
            messages=[
                {"role": "system", "content": "You are a helpful assistant with access to tools."},
                {"role": "user", "content": prompt}
            ],
            tools=formatted_tools,
            max_tokens=params["max_tokens"],
            temperature=params["temperature"]
        )
        
        message = response.choices[0].message
        
        # Check if the model wants to call a tool
        if hasattr(message, 'tool_calls') and message.tool_calls:
            tool_call = message.tool_calls[0]
            return {
                "type": "tool_call",
                "tool": tool_call.function.name,
                "arguments": json.loads(tool_call.function.arguments)
            }
        else:
            return {
                "type": "text",
                "content": message.content
            }

class AnthropicService(LLMService):
    """Anthropic API service"""
    
    def __init__(self, api_key: str, model: str = "claude-2"):
        """Initialize with API key and model"""
        self.api_key = api_key
        self.model = model
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text from a prompt"""
        import anthropic
        
        # Set default parameters
        params = {
            "max_tokens": 1000,
            "temperature": 0.2,
            **kwargs
        }
        
        # Call the API
        client = anthropic.Anthropic(api_key=self.api_key)
        response = client.completions.create(
            model=self.model,
            prompt=f"\n\nHuman: {prompt}\n\nAssistant:",
            max_tokens_to_sample=params["max_tokens"],
            temperature=params["temperature"]
        )
        
        return response.completion
    
    def generate_with_tools(self, prompt: str, tools: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        """Generate text with potential tool calls - note: not all models support this"""
        import anthropic
        import json
        import re
        
        # Claude doesn't have native tool calling, so we use a prompt-based approach
        tools_description = "\n".join([
            f"- {tool['name']}: {tool.get('description', '')}"
            for tool in tools
        ])
        
        tool_prompt = f"""
        You have access to the following tools:
        
        {tools_description}
        
        If you need to use a tool, respond in the following format:
        <tool>
        {{
            "name": "tool_name",
            "arguments": {{
                "arg1": "value1",
                "arg2": "value2"
            }}
        }}
        </tool>
        
        If you don't need to use a tool, respond normally.
        
        Human: {prompt}
        
        Assistant:
        """
        
        # Set default parameters
        params = {
            "max_tokens": 1000,
            "temperature": 0.2,
            **kwargs
        }
        
        # Call the API
        client = anthropic.Anthropic(api_key=self.api_key)
        response = client.completions.create(
            model=self.model,
            prompt=tool_prompt,
            max_tokens_to_sample=params["max_tokens"],
            temperature=params["temperature"]
        )
        
        # Parse the response to check for tool call
        tool_call_match = re.search(r"<tool>(.*?)</tool>", response.completion, re.DOTALL)
        
        if tool_call_match:
            try:
                tool_data = json.loads(tool_call_match.group(1))
                return {
                    "type": "tool_call",
                    "tool": tool_data.get("name", ""),
                    "arguments": tool_data.get("arguments", {})
                }
            except json.JSONDecodeError:
                # If we can't parse the JSON, treat it as regular text
                return {
                    "type": "text",
                    "content": response.completion
                }
        else:
            return {
                "type": "text",
                "content": response.completion
            }

class OllamaService(LLMService):
    """Ollama local LLM service"""
    
    def __init__(self, model: str = "gemma3:4b-it-qat"):
        """Initialize with model name"""
        self.model = model
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text from a prompt"""
        import ollama
        
        # Call the API
        response = ollama.chat(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response['message']['content']
    
    def generate_with_tools(self, prompt: str, tools: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        """Generate text with potential tool calls"""
        import ollama
        import json
        import re
        
        # Format tools for prompt
        tools_description = "\n".join([
            f"- {tool['name']}: {tool.get('description', '')}"
            for tool in tools
        ])
        
        # Create a prompt that instructs the model about tool calling format
        tool_prompt = f"""
        You have access to the following tools:
        
        {tools_description}
        
        If you need to use a tool, respond in the following format:
        ```json
        {{
            "tool": "tool_name",
            "arguments": {{
                "arg1": "value1",
                "arg2": "value2"
            }}
        }}
        ```
        
        If you don't need to use a tool, respond normally.
        
        User query: {prompt}
        """
        
        # Call the API
        response = ollama.chat(
            model=self.model,
            messages=[{"role": "user", "content": tool_prompt}]
        )
        
        response_text = response['message']['content']
        
        # Check for JSON tool call pattern
        json_pattern = r"```json\s*(.*?)\s*```"
        match = re.search(json_pattern, response_text, re.DOTALL)
        
        if match:
            try:
                tool_data = json.loads(match.group(1))
                return {
                    "type": "tool_call",
                    "tool": tool_data.get("tool", ""),
                    "arguments": tool_data.get("arguments", {})
                }
            except json.JSONDecodeError:
                # Fall back to text response if JSON parsing fails
                return {
                    "type": "text",
                    "content": response_text
                }
        else:
            return {
                "type": "text",
                "content": response_text
            }

def get_llm_service(config: Dict[str, Any]) -> LLMService:
    """Factory function to get an LLM service based on configuration"""
    provider = config.get("provider", "ollama").lower()
    
    if provider == "openai":
        api_key = config.get("api_key", "")
        model = config.get("model", "gpt-4")
        return OpenAIService(api_key, model)
    elif provider == "anthropic":
        api_key = config.get("api_key", "")
        model = config.get("model", "claude-2")
        return AnthropicService(api_key, model)
    elif provider == "ollama":
        model = config.get("model", "gemma3:4b-it-qat")
        return OllamaService(model)
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")
