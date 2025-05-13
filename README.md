
# Data Memory System

A modular system for data analysis with memory management, powered by Large Language Models.

## Overview

The Data Memory System integrates large language models with specialized tools to create an intelligent data analysis assistant that can:

1. Remember past interactions and data artifacts
2. Execute SQL queries based on natural language questions
3. Create visualizations that answer specific data exploration goals
4. Summarize datasets and extract key insights
5. Refine visualizations based on user feedback

## Architecture

The system consists of several modular components:

### MCP Servers

- **Memory Server**: Stores and retrieves conversation history and data artifacts
- **SQL Agent Server**: Generates and executes SQL queries
- **Data Visualization Server**: Creates and evaluates Plotly visualizations
- **Data Summarization Server**: Summarizes datasets and generates exploration goals

### Core Components

- **Memory System**: Specialized vector-based memory for conversation history and data artifacts
- **Client**: Orchestrates interaction between servers and user
- **LLM Service**: Interface to language models for intelligence
- **Utils**: Helper functions for data manipulation and safe code execution

## Getting Started

### Prerequisites

- Python 3.9+
- Sentence Transformers
- FAISS or another vector database
- Ollama (for local models)
- SQLite3
- Plotly

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/data-memory-system.git
cd data-memory-system
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up the configuration in `config/llm_config.py` and `config/server_config.py`.

### Running the System

1. Start the interactive console:
```bash
python app/main.py --interactive
```

2. Or use the Gradio UI:
```bash
python app/ui/gradio_app.py
```

## Example Usage

```
You: Summarize the sales data by region
System: Analyzing sales data...
[Visualizations and insights are displayed]

You: Can you change the chart to a bar graph?
System: [Updates visualization to a bar graph]
```

## Project Structure

```
data_memory_system/
│
├── mcp_servers/          # MCP servers for different capabilities
│   ├── memory_server.py
│   ├── sql_agent_server.py
│   ├── data_visualization_server.py
│   └── data_summarization_server.py
│
├── client/               # Client orchestration
│   ├── data_analysis_client.py
│   ├── intent_detection.py
│   └── response_formatter.py
│
├── memory/               # Memory management
│   ├── base.py
│   ├── conversation_memory.py
│   └── data_artifacts.py
│
├── models/               # Model interfaces
│   ├── embeddings.py
│   └── llm.py
│
├── prompts/              # LLM prompts
│   ├── sql_prompts.py
│   ├── visualization_prompts.py
│   └── summarization_prompts.py
│
├── utils/                # Utility functions
│   ├── database.py
│   ├── safe_execution.py
│   └── formatters.py
│
├── config/               # Configuration
│   ├── server_config.py
│   └── llm_config.py
│
└── app/                  # Application entry points
    ├── main.py           # CLI application
    └── ui/               # User interfaces
        └── gradio_app.py # Gradio UI
```

## Extending the System

### Adding New Tools

1. Create a new MCP server in the `mcp_servers` directory
2. Define tool functions using the `@mcp.tool()` decorator
3. Define prompts using the `@mcp.prompt()` decorator
4. Add the server to the configuration in `config/server_config.py`

### Adding New Memory Types

1. Create a new class that extends `memory.base.BaseMemory` or `memory.base.VectorMemory`
2. Implement the required methods: `store`, `retrieve`, `update`, and `delete`
3. Add custom methods for specialized memory operations

## License

This project is licensed under the MIT License - see the LICENSE file for details.
