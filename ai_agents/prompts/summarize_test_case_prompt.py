from typing import List
from template.prompt_template import PromptTemplate

class SummarizeTestCasePrompt:
    def __init__(self):
        self.summarize_prompt = PromptTemplate(
role='You are an EXPERT, MINIMALISTIC, and CLEAR-THINKING test case summarizer.',

instructions='''
You are given a test case with a name, description, and past user responses(newline or ; separated).
Your job is to provide a clear and concise summary of the test case that captures its essential purpose and requirements.

STRICTLY FOLLOW THESE GUIDELINES STRICTLY:
1. Write a detailed and comprehensive summary of the test case using the test case name, description, and past user responses.
2. Identify the tables required to write the SQL query using the test case description and past user responses.
3. Identify key columns involved using the test case description and past user responses.
4. Highlight key filtering conditions or criteria using the test case description and past user responses.
5. Identify ambiguities which are 100% not clear and 100% truly essential to write the SQL query using the test case description and past user responses.
6. Identify technical ambiguities from the past user responses

VERY IMPORTANT:
FINALLY, OVERWRITE OR CLEANUP THE AMBIGUITIES IF YOU FIND THINGS ARE ANSWERED OR NOT REQUIRED BY ANALYZING THE PAST USER RESPONSES.
''',

goal='''
Your goal is to not to overdo the task. Follow the OUTPUT FORMAT STRICTLY. Follow the guidelines strictly.
''',

output_format='''
Respond ONLY with a valid JSON object in the following format and nothing else. Do not include any explanation, markdown, or extra text.:

{
  "summary": "<A detailed and comprehensive summary of the test case using the test case name and description and past user responses>",
  "key_tables": ["<VERY MINIMALISTIC: Identify the main tables (comma separated)>"],
  "key_columns": ["<VERY MINIMALISTIC: Identify key columns (comma separated) using the test case description and past user responses>"],
  "key_criteria": ["<VERY MINIMALISTIC: Highlight key filtering conditions or criteria (comma separated)>"],
  "column_modifications": ["<VERY MINIMALISTIC: Identify the columns to be modified using the test case description and past user responses.>"],
  "ambiguities": ["<VERY MINIMALISTIC: NON-TECHNICAL business rules ambiguities which are 100% not clear and 100% truly essential to write the SQL query (comma separated)>"],
  "select_columns": ["<VERY MINIMALISTIC: Identify the columns to be included in the SELECT clause using the test case description and past user responses.>"],
  "technical_ambiguities": ["<VERY MINIMALISTIC: Identify technical ambiguities from the past user responses (comma separated)>"],
}
''',

examples='''''',
        )
        