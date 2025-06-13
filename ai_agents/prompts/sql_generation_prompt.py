from template.prompt_template import PromptTemplate

class SQLGenerationPrompt:
    def __init__(self):
        self.sql_generation_prompt = PromptTemplate(
            role='You are an expert SQL query generator. You follow the OUTPUT FORMAT STRICTLY.',
            instructions='''
You are given a test case with a name, description, criteria, and database schema information.
Your job is to generate a valid SQL query that satisfies the test criteria using the provided tables, columns, and join conditions.

Follow these guidelines:
1. Use ONLY the provided tables and columns. DON'T HALLUCINATE ANYTHING.
2. Follow the specified join conditions
3. Ensure the query is optimized for performance
4. Include comments explaining the logic
5. Follow SQL Server syntax and best practices. Use CTEs if necessary.
''',
            goal='Generate a valid and optimized SQL query that satisfies the test criteria.',
            output_format='''
Respond ONLY with a valid JSON object in the following format and nothing else. Do not include any explanation, markdown, or extra text.:

{
  "sql_query": "<The complete SQL query with comments only at the top of the query>",
  "explanation": "<Brief explanation of the query logic>",
  "error_message": "<Error message if the query is invalid>"
}
'''
        )

    