
import gradio as gr
import asyncio
import os
import sys
import json

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from client.data_analysis_client import DataAnalysisClient
from config.server_config import MCP_SERVERS

class GradioApp:
    def __init__(self):
        self.client = None
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
    async def init_client(self):
        """Initialize the client and connect to servers"""
        self.client = DataAnalysisClient()
        
        # Connect to servers
        await self.client.connect_to_servers({
            "memory": MCP_SERVERS["memory"]["script_path"],
            "sql": MCP_SERVERS["sql"]["script_path"],
            "visualization": MCP_SERVERS["visualization"]["script_path"],
            "summarization": MCP_SERVERS["summarization"]["script_path"]
        })
        
        return "Client initialized and connected to all servers!"
        
    def handle_query(self, query, chat_history):
        """Handle a user query"""
        if not self.client:
            return "Client not initialized yet. Please try again in a moment.", chat_history
            
        # Process the query
        result = self.loop.run_until_complete(self.client.process_analysis_request(query))
        
        # Extract visualization if available
        visualization_html = ""
        if "visualization_code" in result:
            try:
                # This would execute the visualization code in a safe environment
                # For the demo, we'll just show the code
                visualization_html = f"<pre><code>{result['visualization_code']}</code></pre>"
            except Exception as e:
                visualization_html = f"Error rendering visualization: {str(e)}"
                
        # Format response
        if "error" in result:
            response = f"Error: {result['error']}"
        else:
            if "summary" in result and isinstance(result["summary"], dict) and "overview" in result["summary"]:
                response = f"Analysis: {result['summary']['overview']}"
            else:
                response = "Analysis completed successfully."
            
            if "goals" in result and result["goals"]:
                goals_text = "\n".join([f"- {goal.get('question', '')}" for goal in result["goals"][:3]])
                response += f"\n\nSuggested visualizations:\n{goals_text}"
                
        # Update chat history
        chat_history.append((query, response))
        if visualization_html:
            chat_history.append((None, visualization_html))
            
        return "", chat_history
    
    def build_ui(self):
        """Build and launch the Gradio UI"""
        with gr.Blocks(title="Data Analysis System") as interface:
            gr.Markdown("# Data Analysis System")
            gr.Markdown("Ask questions about your data and get visualizations")
            
            init_button = gr.Button("Initialize Client")
            init_status = gr.Textbox(label="Initialization Status", interactive=False)
            
            chatbot = gr.Chatbot(height=500)
            msg = gr.Textbox(label="Query")
            clear = gr.Button("Clear")
            
            # Set up event handlers
            init_button.click(
                lambda: self.loop.run_until_complete(self.init_client()),
                inputs=[],
                outputs=[init_status]
            )
            
            msg.submit(
                self.handle_query,
                inputs=[msg, chatbot],
                outputs=[msg, chatbot]
            )
            
            clear.click(lambda: None, None, chatbot, queue=False)
            
        # Launch the interface
        interface.launch()
        
    def cleanup(self):
        """Clean up resources"""
        if self.client:
            self.loop.run_until_complete(self.client.cleanup())

# Launch the app
if __name__ == "__main__":
    app = GradioApp()
    try:
        app.build_ui()
    finally:
        app.cleanup()
