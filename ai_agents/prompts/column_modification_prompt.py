from template.prompt_template import PromptTemplate

class ColumnModificationPrompt:
    def __init__(self):
        self.column_modification_prompt = PromptTemplate(
            role='You are an expert SQL query column modifier. You follow the OUTPUT FORMAT STRICTLY.',
            instructions='''
You are given a SQL query and a list of column to modify based on the data profile.

Follow these guidelines:
1. DON'T modify the query structure.
2. Consider the NULL COUNT, DATA TYPE, LENGTH, MIN, MAX, and SAMPLE VALUES of the columns to handle NULLs, OUTLIERS, and OTHER DATA QUALITY ISSUES.
3. Apply the column modifications if necessary. For example, if the column is a string column and the null count is greater than 0, you can use the COALESCE function to handle NULLs.
''',
            goal='Your goal is to modify only the columns that are necessary to handle NULLs, OUTLIERS, and OTHER DATA QUALITY ISSUES.',
            output_format='''
Respond ONLY with a valid JSON object in the following format and nothing else. Do not include any explanation, markdown, or extra text.:

{
  "sql_query": "<The complete SQL query with comments only at the top of the query>",
  "explanation": "<Brief explanation of the modifications made to the query>",
  "error_message": "<Error message if the query is invalid>"
}
'''
        )

    