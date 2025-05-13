from mcp.server.fastmcp import FastMCP
import openai
import json
import sqlite3
from ..prompts.sql_prompts import generation_prompt, refinement_prompt, error_handling_prompt

mcp = FastMCP("sql_agent_server")

@mcp.prompt()
def sql_generation_system_prompt() -> str:
    """System prompt for SQL generation"""
    return generation_prompt()

@mcp.prompt()
def sql_refinement_system_prompt() -> str:
    """System prompt for SQL refinement"""
    return refinement_prompt()

@mcp.tool()
def generate_sql_query(question: str, schema: str) -> str:
    """Generate SQL query based on natural language question and database schema"""
    # Get the prompt
    prompt_template = generation_prompt()
    
    # Format the prompt
    prompt = prompt_template.replace("{{question}}", question).replace("{{schema}}", schema)
    
    # Call LLM
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": prompt}
        ]
    )
    
    # Extract SQL query
    query = response.choices[0].message.content.strip()
    return query

@mcp.tool()
def execute_sql_query(query: str, connection_string: str) -> str:
    """Execute SQL query and return results as JSON"""
    try:
        # Parse connection string (in a real system, would be more secure)
        db_path = connection_string.replace("sqlite:///", "")
        
        # Connect to database
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Execute query
        cursor.execute(query)
        
        # Fetch results
        rows = cursor.fetchall()
        
        # Convert to list of dicts
        results = []
        for row in rows:
            results.append({key: row[key] for key in row.keys()})
        
        # Close connection
        conn.close()
        
        return json.dumps(results)
        
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "query": query
        })

@mcp.tool()
def refine_sql_query(query: str, feedback: str) -> str:
    """Refine SQL query based on feedback"""
    # Get the prompt
    prompt_template = refinement_prompt()
    
    # Format the prompt
    prompt = prompt_template.replace("{{query}}", query).replace("{{feedback}}", feedback)
    
    # Call LLM
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": prompt}
        ]
    )
    
    # Extract refined SQL query
    refined_query = response.choices[0].message.content.strip()
    return refined_query

if __name__ == "__main__":
    mcp.run()