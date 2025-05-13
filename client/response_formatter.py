from typing import Dict, Any, List
import json

class ResponseFormatter:
    """Formats responses for presentation to the user"""
    
    def format_analysis_response(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Format analysis result for presentation"""
        formatted = {
            "text_response": self._generate_text_response(result),
            "visualization": self._extract_visualization(result),
            "data_summary": self._extract_data_summary(result),
            "additional_insights": self._extract_insights(result)
        }
        
        return formatted
    
    def _generate_text_response(self, result: Dict[str, Any]) -> str:
        """Generate natural language response describing the analysis"""
        if "error" in result:
            return f"There was an error processing your request: {result['error']}"
            
        if "visualization_code" in result:
            # For a new analysis
            if "summary" in result and "goals" in result:
                # Extract key information from summary
                summary_data = result.get("summary", {})
                overview = summary_data.get("overview", "")
                
                response = f"I analyzed the data you requested. {overview}\n\n"
                
                # Add information about the visualization
                response += "I've created a visualization that shows "
                
                # If we have goals, mention the primary goal
                if result.get("goals") and len(result["goals"]) > 0:
                    goal = result["goals"][0]
                    question = goal.get("question", "")
                    response += f"information related to: {question}\n\n"
                else:
                    response += "the key patterns in the data.\n\n"
                
                return response
            
            # For a refinement
            elif "original_artifact" in result:
                return f"I've refined the visualization based on your feedback. The original visualization showed {result.get('original_artifact', '')}."
        
        # Default response
        return "Here are the results of your data analysis request."
    
    def _extract_visualization(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract visualization information"""
        if "visualization_code" in result:
            return {
                "code": result["visualization_code"],
                "type": "plotly",
                "is_refinement": "original_artifact" in result
            }
        return {}
    
    def _extract_data_summary(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract data summary information"""
        if "summary" in result:
            return result["summary"]
        return {}
    
    def _extract_insights(self, result: Dict[str, Any]) -> List[str]:
        """Extract additional insights"""
        insights = []
        
        # Extract insights from summary if available
        if "summary" in result and "patterns" in result["summary"]:
            insights.extend(result["summary"]["patterns"])
            
        # Add goals as potential insights
        if "goals" in result and len(result["goals"]) > 1:
            for goal in result["goals"][1:]:  # Skip the first one as it was used for visualization
                insights.append(f"You might also want to explore: {goal.get('question', '')}")
                
        return insights