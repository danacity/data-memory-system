
#!/usr/bin/env python
import os
import sys
import subprocess
import argparse

def main():
    """Run the Data Memory System"""
    parser = argparse.ArgumentParser(description="Run the Data Memory System")
    parser.add_argument("--ui", action="store_true", help="Run with Gradio UI")
    parser.add_argument("--setup", action="store_true", help="Run setup script first")
    parser.add_argument("--query", type=str, help="Run a single query")
    args = parser.parse_args()
    
    # Run setup if requested
    if args.setup:
        print("Running setup script...")
        subprocess.run([sys.executable, "setup.py"])
    
    # Run the appropriate script
    if args.ui:
        print("Starting Gradio UI...")
        subprocess.run([sys.executable, "app/ui/gradio_app.py"])
    elif args.query:
        print(f"Running query: {args.query}")
        subprocess.run([sys.executable, "app/main.py", "--query", args.query])
    else:
        print("Starting interactive console...")
        subprocess.run([sys.executable, "app/main.py", "--interactive"])

if __name__ == "__main__":
    main()
