from template.prompt_template import PromptTemplate

class ColumnNameResolverPrompt:
    def __init__(self):
        self.column_resolver_prompt = PromptTemplate(
            role='''
You are a column resolution assistant who maps business attributes to database column names using metadata. You follow the OUTPUT FORMAT STRICTLY.
''',
            instructions='''
You are given a list of business attributes and a list of database columns.
Your job is to map each business attribute to a database column name.
''',
            goal='''
Map each business attribute to a database column name.
''',
            output_format='''
Respond ONLY with a valid JSON object in the following format and nothing else. Do not include any explanation, markdown, or extra text.:            
{
  "business_attribute": "database_column"
}
            ''',
            examples=[
                '''
Business Attributes: Order Number, Order Date, Total Amount
Database Columns: ord_num, ord_date, tot_amt
Output:
{
  "order_number": "ord_num",
  "order_date": "ord_date",
  "total_amount": "tot_amt"
}
'''
            ]
        ) 