
import asyncio
import argparse
import os
import sys
import json

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from client.data_analysis_client import DataAnalysisClient
from config.server_config import MCP_SERVERS

async def main():
    parser = argparse.ArgumentParser(description="Data Memory System")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    parser.add_argument("--query", type=str, help="Run a single query")
    args = parser.parse_args()
    
    # Create client
    client = DataAnalysisClient()
    
    try:
        # Connect to servers
        print("Connecting to MCP servers...")
        await client.connect_to_servers({
            "memory": MCP_SERVERS["memory"]["script_path"],
            "sql": MCP_SERVERS["sql"]["script_path"],
            "visualization": MCP_SERVERS["visualization"]["script_path"],
            "summarization": MCP_SERVERS["summarization"]["script_path"]
        })
        print("Connected to all servers!")
        
        if args.interactive:
            # Run interactive loop
            await client.chat_loop()
        elif args.query:
            # Run single query
            result = await client.process_analysis_request(args.query)
            print("Result:")
            print(json.dumps(result, indent=2))
        else:
            parser.print_help()
            
    finally:
        # Clean up
        await client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
