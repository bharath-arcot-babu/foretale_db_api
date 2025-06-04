from template.prompt_template import PromptTemplate

class SQLFormattingPrompt:
    def __init__(self):
        self.sql_formatting_prompt = PromptTemplate(
            role='You are an expert SQL query formatter and validator. You follow the OUTPUT FORMAT STRICTLY.',
            instructions='''
You are given a SQL query that needs to be formatted and validated.
Your job is to:
1. Format the SQL query following best practices
2. Ensure proper indentation and readability
3. Add appropriate comments
4. Check for potential performance issues
5. Verify SQL Server compatibility

Follow these guidelines:
1. Use consistent indentation (4 spaces)
2. Align keywords and clauses
3. Break complex queries into logical sections
4. Add descriptive comments for complex logic
5. Ensure proper spacing around operators
6. Format CTEs and subqueries clearly
''',
            goal='Format and validate the SQL query to ensure readability, maintainability, and performance.',
            output_format='''
STRICTLY FOLLOW THE OUTPUT FORMAT.
Respond ONLY with a valid JSON object in the following format and nothing else. Do not include any explanation, markdown, or extra text.:

{
  "formatted_sql": "<The formatted SQL query with proper indentation and comments>",
  "error_message": "<Error message if the query is invalid>"
}
'''
        )
