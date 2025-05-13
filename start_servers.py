
#!/usr/bin/env python
import subprocess
import sys
import time
import os
import signal
import argparse
from config.server_config import MCP_SERVERS

# Global list to keep track of server processes
server_processes = []

def start_server(server_name, server_config):
    """Start an MCP server"""
    script_path = server_config["script_path"]
    port = server_config.get("port", 0)
    
    # Use environment variable to set port if specified
    env = os.environ.copy()
    if port > 0:
        env["MCP_PORT"] = str(port)
    
    try:
        # Start the server as a subprocess
        process = subprocess.Popen(
            [sys.executable, script_path],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        server_processes.append(process)
        
        print(f"Started {server_name} server (PID: {process.pid})")
        return True
    except Exception as e:
        print(f"Error starting {server_name} server: {str(e)}")
        return False

def stop_servers():
    """Stop all running MCP servers"""
    for process in server_processes:
        if process.poll() is None:  # Process is still running
            try:
                # Try to terminate gracefully
                process.terminate()
                time.sleep(0.5)
                
                # Force kill if still running
                if process.poll() is None:
                    process.kill()
            except Exception as e:
                print(f"Error stopping server process: {str(e)}")
    
    print("All servers stopped")

def main():
    """Main function to start MCP servers"""
    parser = argparse.ArgumentParser(description="Start MCP servers")
    parser.add_argument("--selected", type=str, nargs="+", help="Only start specific servers")
    args = parser.parse_args()
    
    print("Starting MCP servers...")
    
    # Register signal handlers to gracefully shut down servers on exit
    signal.signal(signal.SIGINT, lambda sig, frame: handle_shutdown())
    signal.signal(signal.SIGTERM, lambda sig, frame: handle_shutdown())
    
    # Start servers
    started_count = 0
    if args.selected:
        # Start only selected servers
        selected_servers = args.selected
        for server_name in selected_servers:
            if server_name in MCP_SERVERS:
                if start_server(server_name, MCP_SERVERS[server_name]):
                    started_count += 1
            else:
                print(f"Unknown server: {server_name}")
    else:
        # Start all servers
        for server_name, server_config in MCP_SERVERS.items():
            if start_server(server_name, server_config):
                started_count += 1
    
    if started_count > 0:
        print(f"\n{started_count} MCP servers started successfully")
        print("Press Ctrl+C to stop all servers")
        
        # Keep the script running until interrupted
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nReceived interrupt signal, shutting down servers...")
        finally:
            stop_servers()
    else:
        print("No servers were started successfully")
        return 1
    
    return 0

def handle_shutdown():
    """Handle shutdown signals"""
    print("\nShutting down MCP servers...")
    stop_servers()
    sys.exit(0)

if __name__ == "__main__":
    sys.exit(main())
