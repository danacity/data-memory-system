from mcp.server.fastmcp import FastMCP
import openai
import json
from ..prompts.summarization_prompts import dataset_summary_prompt, exploration_goals_prompt, insights_prompt

mcp = FastMCP("data_summarization_server")

@mcp.prompt()
def summarization_system_prompt() -> str:
    """System prompt for data summarization"""
    return dataset_summary_prompt()

@mcp.prompt()
def exploration_system_prompt() -> str:
    """System prompt for exploration goals"""
    return exploration_goals_prompt()

@mcp.tool()
def summarize_dataset(data_json: str) -> str:
    """Create a comprehensive summary of the dataset"""
    # Get the prompt
    prompt_template = dataset_summary_prompt()
    
    # Format the prompt
    prompt = prompt_template.replace("{{data_json}}", data_json)
    
    # Call LLM
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": prompt}
        ]
    )
    
    # Extract summary
    summary = response.choices[0].message.content.strip()
    
    # Validate that it's proper JSON
    try:
        json.loads(summary)
        return summary
    except:
        # If not valid JSON, wrap it
        return json.dumps({"raw_summary": summary})

@mcp.tool()
def generate_exploration_goals(summary: str) -> str:
    """Generate visualization goals based on data summary"""
    # Get the prompt
    prompt_template = exploration_goals_prompt()
    
    # Format the prompt
    prompt = prompt_template.replace("{{summary}}", summary)
    
    # Call LLM
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": prompt}
        ]
    )
    
    # Extract goals
    goals = response.choices[0].message.content.strip()
    
    # Validate that it's proper JSON
    try:
        json.loads(goals)
        return goals
    except:
        # If not valid JSON, wrap it
        return json.dumps({"raw_goals": goals})

@mcp.tool()
def extract_insights(code: str, data_json: str) -> str:
    """Extract insights from a visualization"""
    # Get the prompt
    prompt_template = insights_prompt()
    
    # Format the prompt
    prompt = prompt_template.replace("{{code}}", code).replace("{{data_json}}", data_json)
    
    # Call LLM
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": prompt}
        ]
    )
    
    # Extract insights
    insights = response.choices[0].message.content.strip()
    
    # Validate that it's proper JSON
    try:
        json.loads(insights)
        return insights
    except:
        # If not valid JSON, wrap it
        return json.dumps({"raw_insights": insights})

if __name__ == "__main__":
    mcp.run()