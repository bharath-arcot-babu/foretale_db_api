from template.prompt_template import PromptTemplate

class TableNameResolverPrompt:
    def __init__(self):
        self.table_resolver_prompt = PromptTemplate(
            role='''
You are a table resolution assistant who maps key tables to database table names using metadata. You must follow the OUTPUT FORMAT STRICTLY.
''',
            instructions='''  
You are given a list of key tables with descriptions and a list of target database tables.
Your task is to map each key table to the most appropriate target database table name using the metadata.
''',
            goal='''
Map each key table to its corresponding target database table name.
''',
            output_format='''
Respond ONLY with a valid JSON object in the following format and nothing else.
Do NOT include any explanation, markdown, or extra text.

{
  "key_table_1": "target_table_name_1",
  "key_table_2": "target_table_name_2"
}
'''
        )