from mcp.server.fastmcp import FastMCP
import openai
import json
from ..prompts.visualization_prompts import generation_prompt, evaluation_prompt, refinement_prompt

mcp = FastMCP("data_visualization_server")

@mcp.prompt()
def visualization_generation_system_prompt() -> str:
    """System prompt for visualization generation"""
    return generation_prompt()

@mcp.prompt()
def visualization_evaluation_system_prompt() -> str:
    """System prompt for visualization evaluation"""
    return evaluation_prompt()

@mcp.tool()
def generate_visualization(data_json: str, goal: str) -> str:
    """Generate Plotly visualization code based on data and goal"""
    # Get the prompt
    prompt_template = generation_prompt()
    
    # Format the prompt
    prompt = prompt_template.replace("{{data_json}}", data_json).replace("{{goal}}", goal)
    
    # Call LLM
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": prompt}
        ]
    )
    
    # Extract visualization code
    viz_code = response.choices[0].message.content.strip()
    return viz_code

@mcp.tool()
def evaluate_visualization(code: str, data_json: str, goal: str) -> str:
    """Evaluate visualization quality across multiple dimensions"""
    # Get the prompt
    prompt_template = evaluation_prompt()
    
    # Format the prompt
    prompt = prompt_template.replace("{{code}}", code).replace("{{data_json}}", data_json).replace("{{goal}}", goal)
    
    # Call LLM
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": prompt}
        ]
    )
    
    # Extract evaluation
    evaluation = response.choices[0].message.content.strip()
    return evaluation

@mcp.tool()
def refine_visualization(code: str, feedback: str, data_json: str) -> str:
    """Refine visualization based on feedback"""
    # Get the prompt
    prompt_template = refinement_prompt()
    
    # Format the prompt
    prompt = prompt_template.replace("{{code}}", code).replace("{{feedback}}", feedback).replace("{{data_json}}", data_json)
    
    # Call LLM
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": prompt}
        ]
    )
    
    # Extract refined code
    refined_code = response.choices[0].message.content.strip()
    return refined_code

@mcp.tool()
def render_visualization(code: str) -> str:
    """Execute Plotly visualization code and return as HTML"""
    try:
        # In a real system, this would execute the code in a sandbox
        # and capture the HTML output
        # For this example, we'll return a placeholder
        return "<div>Visualization would be rendered here</div>"
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "code": code
        })

if __name__ == "__main__":
    mcp.run()