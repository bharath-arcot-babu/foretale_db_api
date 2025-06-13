from prompts.column_modification_prompt import ColumnModificationPrompt
from layer_llm_service.bedrock_langchain_utils import BedrockLangChainService

class ColumnModifierTool:
    def __init__(self):
        self.llm = BedrockLangChainService().get_llm()
        self.prompt = ColumnModificationPrompt()

    def apply_column_modifications(self, sql_query: str, column_with_data_profile: list) -> str:
        """
        Applies column modifications to the SQL query based on the data profile.
        
        Args:
            sql_query: The SQL query to modify
            column_with_data_profile: List of columns with data profile
        
        Returns:
            str: The modified SQL query
        """
        prompt = self.prompt.column_modification_prompt.build_prompt_template_apply_column_modifications(
            sql_query=sql_query,
            column_with_data_profile=column_with_data_profile
        )
        response = BedrockLangChainService().call_llm_general_purpose(prompt)
        
        return response
        