
#!/usr/bin/env python
import os
import sys
import importlib.util
import asyncio

def check_directories():
    """Check if all required directories exist"""
    required_dirs = [
        "",  # Base directory
        "mcp_servers",
        "client",
        "memory",
        "models",
        "prompts",
        "utils",
        "config",
        "app",
        "app/ui"
    ]
    
    missing_dirs = []
    for dir_path in required_dirs:
        full_path = dir_path  # Already relative to current directory
        if not os.path.isdir(full_path):
            missing_dirs.append(full_path)
    
    if missing_dirs:
        print("❌ Missing directories:")
        for dir_path in missing_dirs:
            print(f"  - {dir_path}")
        return False
    else:
        print("✅ All required directories exist")
        return True

def check_files():
    """Check if all required files exist"""
    required_files = [
        # MCP servers
        "mcp_servers/__init__.py",
        "mcp_servers/memory_server.py",
        "mcp_servers/sql_agent_server.py",
        "mcp_servers/data_visualization_server.py",
        "mcp_servers/data_summarization_server.py",
        
        # Client
        "client/__init__.py",
        "client/data_analysis_client.py",
        "client/intent_detection.py",
        "client/response_formatter.py",
        
        # Memory
        "memory/__init__.py",
        "memory/base.py",
        "memory/conversation_memory.py",
        "memory/data_artifacts.py",
        
        # Models
        "models/__init__.py",
        "models/embeddings.py",
        "models/llm.py",
        
        # Prompts
        "prompts/__init__.py",
        "prompts/sql_prompts.py",
        "prompts/visualization_prompts.py",
        "prompts/summarization_prompts.py",
        
        # Utils
        "utils/__init__.py",
        "utils/database.py",
        "utils/safe_execution.py",
        "utils/formatters.py",
        
        # Config
        "config/__init__.py",
        "config/server_config.py",
        "config/llm_config.py",
        
        # App
        "app/__init__.py",
        "app/main.py",
        "app/ui/__init__.py",
        "app/ui/gradio_app.py",
        
        # Project files
        "README.md",
        "requirements.txt",
        "setup.py",
        "run.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        full_path = file_path  # Already relative to current directory
        if not os.path.isfile(full_path):
            missing_files.append(full_path)
    
    if missing_files:
        print("❌ Missing files:")
        for file_path in missing_files:
            print(f"  - {file_path}")
        return False
    else:
        print("✅ All required files exist")
        return True

def check_imports():
    """Check if required Python packages can be imported"""
    required_packages = [
        "mcp",  # pip install mcp
        "sentence_transformers",  # pip install sentence-transformers
        "numpy",
        "json",
        "sqlite3",
        "asyncio"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            spec = importlib.util.find_spec(package)
            if spec is None:
                missing_packages.append(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing Python packages:")
        for package in missing_packages:
            print(f"  - {package}")
        print("\nInstall missing packages with:")
        print("pip install " + " ".join(missing_packages))
        return False
    else:
        print("✅ All required Python packages can be imported")
        return True

def check_config():
    """Check if configuration files are valid"""
    try:
        from config.server_config import MCP_SERVERS
        from config.llm_config import get_active_llm_config
        
        # Check if MCP_SERVERS has the required keys
        required_servers = ["memory", "sql", "visualization", "summarization"]
        missing_servers = [server for server in required_servers if server not in MCP_SERVERS]
        
        if missing_servers:
            print(f"❌ Missing servers in config: {', '.join(missing_servers)}")
            return False
            
        # Check if llm_config can be loaded
        config = get_active_llm_config()
        if not isinstance(config, dict):
            print("❌ LLM configuration is not a dictionary")
            return False
            
        print("✅ Configuration files are valid")
        return True
    except Exception as e:
        print(f"❌ Error checking configuration: {str(e)}")
        return False

async def run_basic_test():
    """Run a basic test to check if client can be initialized"""
    try:
        sys.path.insert(0, os.path.abspath('.'))
        
        # Check if the client can be imported
        from client.data_analysis_client import DataAnalysisClient
        
        # Create client
        client = DataAnalysisClient()
        print("✅ Client created successfully")
        
        # Note: We don't actually connect to servers here since they may not be running
        print("✓ Basic client initialization successful")
        return True
    except Exception as e:
        print(f"❌ Error during basic test: {str(e)}")
        return False

def main():
    """Main verification function"""
    print("Verifying Data Memory System...")
    
    # Check directories
    dirs_ok = check_directories()
    
    # Check files
    files_ok = check_files()
    
    # Check imports (optional depending on environment)
    imports_ok = check_imports()
    
    # Check configuration
    config_ok = check_config()
    
    # Run basic test
    test_ok = asyncio.run(run_basic_test())
    
    # Overall verification result
    if all([dirs_ok, files_ok, config_ok, test_ok]):
        print("\n✅ Verification completed successfully - system is ready to run!")
        print("\nTo run the system:")
        print("1. Run setup: python setup.py")
        print("2. Start the application: python run.py")
        return 0
    else:
        print("\n❌ Verification failed - please fix the issues above before running the system")
        return 1

if __name__ == "__main__":
    sys.exit(main())
