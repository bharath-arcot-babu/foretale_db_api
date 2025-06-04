import re
from prompts.summarize_test_case_prompt import SummarizeTestCasePrompt
from layer_llm_service.bedrock_langchain_utils import BedrockLangChainService

class TestCaseSummarizer:
    def summarize(self, test_case: str, test_description: str, past_user_responses: str) -> str:
        """
        Summarizes a test case into a JSON structure: summary, key entities, key criteria.
        """
        prompt = SummarizeTestCasePrompt().summarize_prompt.build_prompt_template_summarize_test_case(
            test_case, 
            test_description, 
            past_user_responses)
        
        response = BedrockLangChainService().call_llm_general_purpose(prompt)

        return response
