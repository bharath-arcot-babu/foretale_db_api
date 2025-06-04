from prompts.sql_generation_prompt import SQLGenerationPrompt
from layer_llm_service.bedrock_langchain_utils import BedrockLangChainService

class SQLGenerationTool:
    def generate_sql(
        self, 
        test_summary: str, 
        criteria: str,
        table_hints: str,
        column_hints: str,
        join_hints: str,
        schema_name: str
    ) -> str:
        """
        Generates a SQL query based on the test case, description, criteria, and various hints.
        
        Args:
            test_summary: Summary of the test case
            criteria: Criteria that the SQL query should satisfy
            table_hints: Hints about which tables to use
            column_hints: Hints about which columns to use
            join_hints: Hints about how to join the tables
            
        Returns:
            str: The generated SQL query
        """
        prompt = SQLGenerationPrompt().sql_generation_prompt.build_prompt_template_generate_sql(
            test_summary=test_summary,
            criteria=criteria,
            table_hints=table_hints,
            column_hints=column_hints,
            join_hints=join_hints,
            schema_name=schema_name
        )
        
        response = BedrockLangChainService().call_llm_general_purpose(prompt)
        
        return response