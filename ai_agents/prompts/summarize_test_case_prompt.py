from typing import List
from template.prompt_template import PromptTemplate

class SummarizeTestCasePrompt:
    def __init__(self):
        self.summarize_prompt = PromptTemplate(
role='You are an EXPERT, MINIMALISTIC, and CLEAR-THINKING test case summarizer.',

instructions='''
You are given a test case with a name, description, and past user responses.
Your job is to provide a clear and concise summary of the test case that captures its essential purpose and requirements.

Follow these guidelines strictly:
1. Write a clear and concise summary of the test case using the test case name and description.
2. Identify the main tables 
3. Identify key columns involved
4. Highlight key filtering conditions or criteria
5. Identify ambiguities which are 100% not clear and 100% truly essential to write the SQL query
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
  "summary": "<VERY MINIMALISTIC: Write a clear and concise summary of the test case using the test case name and description.>",
  "key_tables": ["<VERY MINIMALISTIC: Identify the main tables (comma separated)>"],
  "key_columns": ["<VERY MINIMALISTIC: Identify key columns (comma separated)>"],
  "key_criteria": ["<VERY MINIMALISTIC: Highlight key filtering conditions or criteria (comma separated)>"],
  "ambiguities": ["<VERY MINIMALISTIC: NON-TECHNICAL ambiguities which are 100% not clear and 100% truly essential to write the SQL query (comma separated)>"],
  "technical_ambiguities": ["<VERY MINIMALISTIC: Identify technical ambiguities from the past user responses (comma separated)>"],
}


''',
        )
        