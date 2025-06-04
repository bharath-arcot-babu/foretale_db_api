from template.prompt_template import PromptTemplate

class SQLValidationPrompt:
    def __init__(self):
        self.sql_validation_prompt = PromptTemplate(
            role='You are an expert SQL query validator. You follow the OUTPUT FORMAT STRICTLY.',
            instructions='''
You are given a SQL query. Your primary job is to validate the SQL query for syntax correctness and best practices.

Follow these guidelines:
1. Check for SQL syntax errors - this is the highest priority
2. If any syntax errors are found, you MUST provide a corrected version
3. Ensure proper table and column usage
4. Check for potential performance issues
5. Validate join conditions
6. Look for SQL injection vulnerabilities
7. Verify proper use of SQL Server specific features

IMPORTANT: If the query contains any syntax errors, you MUST provide a corrected version that fixes all syntax issues.
''',
            goal='Validate the SQL query for syntax correctness and best practices. If any syntax errors are found, provide a corrected query.',
            output_format='''
Respond ONLY with a valid JSON object in the following format and nothing else. Do not include any explanation, markdown, or extra text.:

{
  "is_valid": true/false,
  "corrected_query": "<The corrected SQL query if any syntax errors are found, otherwise null>"
}
''',
            examples=[
'''
Test Case: Find purchase orders with amount > 10000
SQL Query: SELECT * FROM PurchaseOrders WHERE Amount > 10000

{
  "is_valid": true,
  "corrected_query": null
}
'''
            ]
        ) 