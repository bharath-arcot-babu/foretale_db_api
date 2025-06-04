from prompts.column_name_resolver_prompt import ColumnNameResolverPrompt
from layer_llm_service.bedrock_langchain_utils import BedrockLangChainService

class ColumnResolverTool:

    def resolve_columns(self, business_attributes: str, target_table_columns: str) -> str:
        """
        Resolves a list of business attributes to a list of database columns.
        Returns a JSON string with the mapping.
        """
        prompt = ColumnNameResolverPrompt().column_resolver_prompt.build_prompt_template_column_resolver(
            business_attributes=business_attributes,
            target_table_columns=target_table_columns
        )
        
        response = BedrockLangChainService().call_llm_general_purpose(prompt)
        
        return response
