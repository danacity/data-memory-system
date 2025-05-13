
import json
from typing import Dict, Any, List, Optional

class DataFormatter:
    """Format data for presentation"""
    
    def format_table_preview(self, data: str, max_rows: int = 5) -> str:
        """Format table data as a readable preview"""
        try:
            parsed_data = json.loads(data)
            
            if not isinstance(parsed_data, list) or not parsed_data:
                return "No data to preview"
                
            # Get column names
            columns = list(parsed_data[0].keys())
            
            # Build header
            header = " | ".join(columns)
            separator = "-" * len(header)
            
            # Build rows
            rows = []
            for row in parsed_data[:max_rows]:
                row_str = " | ".join(str(row.get(col, "")) for col in columns)
                rows.append(row_str)
                
            # Combine all parts
            preview = f"{header}\n{separator}\n"
            preview += "\n".join(rows)
            
            # Add count info
            if len(parsed_data) > max_rows:
                preview += f"\n\n(Showing {max_rows} of {len(parsed_data)} rows)"
                
            return preview
            
        except json.JSONDecodeError:
            return "Unable to parse data as JSON"
        except Exception as e:
            return f"Error formatting data: {str(e)}"
    
    def format_summary_highlights(self, summary: Dict[str, Any]) -> List[str]:
        """Extract and format key highlights from a data summary"""
        highlights = []
        
        # Add dataset size
        if "total_rows" in summary:
            highlights.append(f"Dataset contains {summary['total_rows']} records")
            
        # Add column count
        if "columns" in summary:
            highlights.append(f"Dataset has {len(summary['columns'])} columns")
            
        # Add key metrics
        if "statistics" in summary and "key_metrics" in summary["statistics"]:
            for metric, value in summary["statistics"]["key_metrics"].items():
                if isinstance(value, dict) and "value" in value:
                    unit = value.get("unit", "")
                    highlights.append(f"{metric.replace('_', ' ').title()}: {value['value']} {unit}")
                else:
                    highlights.append(f"{metric.replace('_', ' ').title()}: {value}")
                    
        # Add patterns
        if "patterns" in summary:
            highlights.extend(summary["patterns"])
            
        return highlights
