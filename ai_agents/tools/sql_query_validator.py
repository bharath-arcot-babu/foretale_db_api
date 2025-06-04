from prompts.sql_validation_prompt import SQLValidationPrompt
from layer_llm_service.bedrock_langchain_utils import BedrockLangChainService

class SQLQueryValidator:
    def validate_sql(
        self,
        sql_query: str,
        test_case: str,
        test_description: str,
        criteria: str
    ) -> str:
        """
        Validates a SQL query for correctness, syntax, and best practices.
        
        Args:
            sql_query: The SQL query to validate
            test_case: The test case identifier
            test_description: Description of what the test is trying to achieve
            criteria: Criteria that the SQL query should satisfy
            
        Returns:
            str: JSON string containing validation results including errors, warnings, and performance notes
        """
        prompt = SQLValidationPrompt().sql_validation_prompt.build_prompt_template_validate_sql(
            sql_query=sql_query,
            test_case=test_case,
            test_description=test_description,
            criteria=criteria
        )
        
        response = BedrockLangChainService().call_llm_general_purpose(prompt)
        
        return response

if __name__ == "__main__":
    validator = SQLQueryValidator()
    result = validator.validate_sql(
        sql_query="SELECT * FROM PurchaseOrders WHERE Amount >< 10000",
        test_case="TC001",
        test_description="Find purchase orders with amount greater than 10000",
        criteria="Amount must be greater than 10000"
    )
    print(result)
