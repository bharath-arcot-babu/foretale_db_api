from prompts.table_name_resolver_prompt import TableNameResolverPrompt
from layer_llm_service.bedrock_langchain_utils import BedrockLangChainService

class TableResolverTool:

    def resolve_tables(self, key_tables: str, database_tables: str) -> str:
        """
        Resolves a list of business entities to a list of database tables.
        """
        prompt = TableNameResolverPrompt().table_resolver_prompt.build_prompt_template_table_resolver(
            key_tables, 
            database_tables)
        
        response = BedrockLangChainService().call_llm_general_purpose(prompt)
        
        return response
    