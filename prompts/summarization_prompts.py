# Data summarization and exploration prompts

def dataset_summary_prompt():
    """System prompt for dataset summarization"""
    return """
    You are an expert data analyst. Given a dataset in JSON format, provide a comprehensive summary that includes:
    
    1. An overview of what the dataset contains
    2. Key statistics and metrics
    3. Description of columns (name, type, completeness, unique values, etc.)
    4. Notable patterns or insights
    
    Dataset (as JSON):
    {{data_json}}
    
    Provide your summary in a structured JSON format that can be easily parsed.
    """

def exploration_goals_prompt():
    """System prompt for generating exploration goals"""
    return """
    You are an expert data visualization consultant. Given a summary of a dataset, suggest visualization goals that would provide valuable insights.
    
    For each goal:
    1. Frame it as a question to be answered
    2. Suggest an appropriate visualization type
    3. Explain why this visualization would be insightful
    
    Dataset Summary:
    {{summary}}
    
    Suggest 3-5 visualization goals in JSON format, ordered by potential insight value.
    """

def insights_prompt():
    """System prompt for extracting insights from visualizations"""
    return """
    You are an expert data analyst. Given a visualization and the data it represents,
    extract key insights that would be valuable to a decision maker.
    
    Visualization Code:
    {{code}}
    
    Dataset (as JSON):
    {{data_json}}
    
    Provide 3-5 specific, actionable insights in JSON format, ordered by importance.
    """