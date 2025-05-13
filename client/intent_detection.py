from typing import Dict, Any
import re

class IntentDetector:
    """Detects user intent from queries"""
    
    def __init__(self):
        pass
    
    def detect_intent(self, query: str) -> Dict[str, Any]:
        """Detect intent from user query"""
        query_lower = query.lower()
        
        # Check for refinement intent
        refinement_patterns = [
            r"change",
            r"modify",
            r"update",
            r"refine",
            r"adjust",
            r"improve",
            r"fix",
            r"better",
            r"instead",
            r"rather",
            r"different"
        ]
        
        if any(re.search(pattern, query_lower) for pattern in refinement_patterns):
            return {
                "type": "refinement",
                "confidence": 0.8,
                "original_query": self._find_original_query(query)
            }
        
        # SQL intent
        sql_patterns = [
            r"sql",
            r"query",
            r"database",
            r"table",
            r"select",
            r"from",
            r"where",
            r"join"
        ]
        
        if any(re.search(pattern, query_lower) for pattern in sql_patterns):
            return {
                "type": "new_analysis",
                "subtype": "sql_focused",
                "confidence": 0.9
            }
        
        # Visualization intent
        viz_patterns = [
            r"visualize",
            r"visualization",
            r"chart",
            r"graph",
            r"plot",
            r"diagram",
            r"show me"
        ]
        
        if any(re.search(pattern, query_lower) for pattern in viz_patterns):
            return {
                "type": "new_analysis",
                "subtype": "visualization_focused",
                "confidence": 0.9
            }
        
        # Summary intent
        summary_patterns = [
            r"summarize",
            r"summary",
            r"overview",
            r"describe",
            r"explain"
        ]
        
        if any(re.search(pattern, query_lower) for pattern in summary_patterns):
            return {
                "type": "new_analysis",
                "subtype": "summary_focused",
                "confidence": 0.8
            }
        
        # Default to general analysis
        return {
            "type": "new_analysis",
            "subtype": "general",
            "confidence": 0.6
        }
    
    def _find_original_query(self, refinement_query: str) -> str:
        """Find the original query that this refinement refers to - placeholder"""
        return "original query"