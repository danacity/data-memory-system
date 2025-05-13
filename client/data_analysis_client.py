import asyncio
from typing import Dict, Any, List, Optional
import json
import uuid
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from .intent_detection import IntentDetector

class DataAnalysisClient:
    def __init__(self):
        self.memory_session = None
        self.sql_session = None
        self.visualization_session = None
        self.summarization_session = None
        self.exit_stack = AsyncExitStack()
        self.user_id = str(uuid.uuid4())
        
        # Initialize components
        self.intent_detector = IntentDetector()
        
        # State
        self.last_query = ""
        self.last_data_artifacts = []
        
    async def connect_to_servers(self, server_paths):
        """Connect to all required MCP servers"""
        self.memory_session = await self._connect_to_server(server_paths["memory"])
        self.sql_session = await self._connect_to_server(server_paths["sql"])
        self.visualization_session = await self._connect_to_server(server_paths["visualization"])
        self.summarization_session = await self._connect_to_server(server_paths["summarization"])
    
    async def _connect_to_server(self, server_path):
        """Connect to an MCP server"""
        server_params = StdioServerParameters(
            command="python",
            args=[server_path],
            env=None
        )

        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        stdio, write = stdio_transport
        session = await self.exit_stack.enter_async_context(ClientSession(stdio, write))
        await session.initialize()
        
        return session
    
    async def process_analysis_request(self, user_input: str) -> Dict[str, Any]:
        """Process a data analysis request end-to-end"""
        # 1. Store user request in memory
        memory_id = await self.memory_session.call_tool('store_memory', {
            "text": user_input,
            "user_id": self.user_id,
            "memory_type": "analysis_request"
        })
        
        # 2. Analyze user intent
        intent = self.intent_detector.detect_intent(user_input)
        
        # For a new analysis request
        if intent["type"] == "new_analysis":
            # 3a. Generate SQL query
            query = await self.sql_session.call_tool('generate_sql_query', {
                "question": user_input,
                "schema": self._get_database_schema()
            })
            
            # 3b. Execute SQL query
            result_json = await self.sql_session.call_tool('execute_sql_query', {
                "query": query,
                "connection_string": self._get_connection_string()
            })
            
            # 3c. Summarize dataset
            summary = await self.summarization_session.call_tool('summarize_dataset', {
                "data_json": result_json
            })
            
            # 3d. Generate visualization goals
            goals = await self.summarization_session.call_tool('generate_exploration_goals', {
                "summary": summary
            })
            
            # 3e. Select most relevant goal
            selected_goal = self._select_goal(goals, user_input)
            
            # 3f. Generate visualization
            viz_code = await self.visualization_session.call_tool('generate_visualization', {
                "data_json": result_json,
                "goal": selected_goal
            })
            
            # 3g. Evaluate visualization
            evaluation = await self.visualization_session.call_tool('evaluate_visualization', {
                "code": viz_code,
                "data_json": result_json,
                "goal": selected_goal
            })
            
            # 3h. Refine if needed
            eval_data = json.loads(evaluation)
            if "scores" in eval_data and "overall" in eval_data["scores"] and eval_data["scores"]["overall"] < 0.8:
                viz_code = await self.visualization_session.call_tool('refine_visualization', {
                    "code": viz_code,
                    "feedback": eval_data["feedback"],
                    "data_json": result_json
                })
            
            # 3i. Store results in memory
            await self.memory_session.call_tool('store_data_artifact', {
                "memory_id": memory_id,
                "data_type": "query_result",
                "data_content": result_json,
                "summary": f"Data for: {user_input}"
            })
            
            await self.memory_session.call_tool('store_data_artifact', {
                "memory_id": memory_id,
                "data_type": "visualization",
                "data_content": viz_code,
                "summary": f"Visualization for: {selected_goal}"
            })
            
            # 3j. Generate response
            return {
                "query": query,
                "data": json.loads(result_json) if isinstance(result_json, str) else result_json,
                "summary": json.loads(summary) if isinstance(summary, str) else summary,
                "visualization_code": viz_code,
                "goals": json.loads(goals)["goals"] if isinstance(goals, str) and "goals" in json.loads(goals) else []
            }
            
        # For a refinement request
        elif intent["type"] == "refinement":
            # Get relevant data artifacts
            artifacts_json = await self.memory_session.call_tool('retrieve_data_artifacts', {
                "query": user_input,
                "user_id": self.user_id
            })
            
            artifacts = json.loads(artifacts_json)["artifacts"]
            
            if not artifacts:
                return {"error": "No relevant data found for refinement"}
            
            # Find most relevant artifact
            artifact = artifacts[0]
            
            # Refine visualization based on user input
            refined_viz_code = await self.visualization_session.call_tool('refine_visualization', {
                "code": artifact["data_content"],
                "feedback": user_input,
                "data_json": self._get_artifact_data(artifact["memory_id"])
            })
            
            # Store refined visualization
            await self.memory_session.call_tool('store_data_artifact', {
                "memory_id": memory_id,
                "data_type": "visualization",
                "data_content": refined_viz_code,
                "summary": f"Refined visualization based on: {user_input}"
            })
            
            return {
                "visualization_code": refined_viz_code,
                "original_artifact": artifact["summary"]
            }
            
        else:
            return {"error": f"Unsupported intent type: {intent['type']}"}
    
    def _get_database_schema(self):
        """Get database schema - placeholder"""
        return json.dumps({
            "tables": [
                {
                    "name": "sales",
                    "columns": [
                        {"name": "date", "type": "DATE"},
                        {"name": "product_id", "type": "INTEGER"},
                        {"name": "region", "type": "TEXT"},
                        {"name": "amount", "type": "REAL"}
                    ]
                },
                {
                    "name": "products",
                    "columns": [
                        {"name": "id", "type": "INTEGER"},
                        {"name": "name", "type": "TEXT"},
                        {"name": "category", "type": "TEXT"},
                        {"name": "price", "type": "REAL"}
                    ]
                }
            ]
        })
    
    def _get_connection_string(self):
        """Get database connection string - placeholder"""
        return "sqlite:///example.db"
    
    def _get_artifact_data(self, memory_id):
        """Get data associated with an artifact - placeholder"""
        return json.dumps([{"placeholder": "data"}])
    
    def _select_goal(self, goals_json, user_input):
        """Select most relevant visualization goal based on user input"""
        goals = json.loads(goals_json) if isinstance(goals_json, str) else goals_json
        if "goals" in goals and goals["goals"]:
            # In a real system, would use semantic similarity to find best match
            return goals["goals"][0]["question"]
        return "Visualize the data"
    
    async def chat_loop(self):
        """Interactive chat loop"""
        print("\nData Analysis Client Started!")
        print("Type your data analysis queries or 'quit' to exit.")

        while True:
            try:
                user_input = input("\nYou: ").strip()
                
                if user_input.lower() in ['q', 'quit', 'exit']:
                    break

                result = await self.process_analysis_request(user_input)
                
                print("\nResult:")
                print(json.dumps(result, indent=2))

            except Exception as e:
                print(f"\nError: {str(e)}")
                import traceback
                traceback.print_exc()

    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()