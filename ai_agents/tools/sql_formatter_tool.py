from prompts.sql_formatting_prompt import SQLFormattingPrompt
from layer_llm_service.bedrock_langchain_utils import BedrockLangChainService

class SQLFormatterTool:
    def format_sql(self, sql_query: str) -> str:
        """
        Formats a SQL query to make it more readable and consistent.
        
        Args:
            sql_query: The SQL query to be formatted
            
        Returns:
            str: The formatted SQL query
        """
        prompt = SQLFormattingPrompt().sql_formatting_prompt.build_prompt_template_format_sql(
            sql_query=sql_query
            )
        
        response = BedrockLangChainService().call_llm_general_purpose(prompt)
        
        return response
