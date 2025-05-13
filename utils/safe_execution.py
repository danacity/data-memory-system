
import subprocess
import tempfile
import os
import json
from typing import Dict, Any, Optional

class CodeExecutor:
    """Safely execute generated code in a sandboxed environment"""
    
    def execute_plotly(self, code: str) -> Optional[str]:
        """Execute Plotly visualization code and return HTML"""
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a Python file with the code
            script_path = os.path.join(tmpdir, "visualization.py")
            with open(script_path, "w") as f:
                # Add necessary imports
                f.write("import plotly.graph_objects as go\n")
                f.write("import plotly.express as px\n")
                f.write("import json\n\n")
                
                # Add the code
                f.write(code)
                
                # Add code to save the figure as HTML
                f.write("\n\n# Save the figure\n")
                f.write("if 'fig' in locals():\n")
                f.write("    fig.write_html('output.html')\n")
                f.write("else:\n")
                f.write("    print('No figure named "fig" was created')\n")
            
            # Execute the script in a subprocess with timeout
            try:
                subprocess.run(
                    ["python", script_path],
                    cwd=tmpdir,
                    timeout=10,
                    check=True,
                    capture_output=True
                )
                
                # Check if the output file was created
                output_path = os.path.join(tmpdir, "output.html")
                if os.path.exists(output_path):
                    with open(output_path, "r") as f:
                        return f.read()
                        
            except subprocess.TimeoutExpired:
                return None
            except subprocess.CalledProcessError as e:
                # Return error information
                return json.dumps({
                    "error": "Execution failed",
                    "stdout": e.stdout.decode("utf-8"),
                    "stderr": e.stderr.decode("utf-8")
                })
                
        return None
    
    def execute_sql(self, query: str, db_path: str) -> Optional[Dict[str, Any]]:
        """Execute SQL query in a sandboxed environment"""
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a Python file with the code
            script_path = os.path.join(tmpdir, "query.py")
            with open(script_path, "w") as f:
                f.write("import sqlite3\n")
                f.write("import json\n\n")
                
                f.write(f"conn = sqlite3.connect('{db_path}')\n")
                f.write("conn.row_factory = sqlite3.Row\n")
                f.write("cursor = conn.cursor()\n\n")
                
                f.write(f"cursor.execute(""""{query}"""")\n\n")
                
                f.write("rows = cursor.fetchall()\n")
                f.write("result = []\n")
                f.write("for row in rows:\n")
                f.write("    result.append({key: row[key] for key in row.keys()})\n\n")
                
                f.write("print(json.dumps(result))\n")
                f.write("conn.close()\n")
            
            # Execute the script in a subprocess with timeout
            try:
                result = subprocess.run(
                    ["python", script_path],
                    timeout=10,
                    check=True,
                    capture_output=True
                )
                
                # Parse the output
                return json.loads(result.stdout.decode("utf-8"))
                
            except subprocess.TimeoutExpired:
                return {"error": "Query execution timed out"}
            except subprocess.CalledProcessError as e:
                return {
                    "error": "Query execution failed",
                    "details": e.stderr.decode("utf-8")
                }
            except json.JSONDecodeError:
                return {"error": "Failed to parse query results"}
                
        return {"error": "Unknown error executing query"}
