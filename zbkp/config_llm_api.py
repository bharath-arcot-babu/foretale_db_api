"""
Configuration file for LLM API endpoints and settings.
"""

from enum import Enum

class BedrockModel(Enum):
    CLAUDE3 = "anthropic.claude-3-sonnet-20240229-v1:0"
    LLAMA3 = "meta.llama3-70b-instruct-v1:0"
    MISTRAL = "mistral.mistral-large-2402-v1:0"

class LLMApiConfig:
    # AWS Region
    AWS_REGION = "us-east-1"

    # Base URLs for different LLM services
    BASE_MISTRAL_URL = "https://pw4lylhb3g.execute-api.us-east-1.amazonaws.com/dev/bedrock_invoker_resource"
    BASE_LLAMA_URL = "https://0btp5b2cp3.execute-api.ap-south-1.amazonaws.com/dev/bedrock_resource"
    BASE_CLAUDE_URL = "https://0btp5b2cp3.execute-api.ap-south-1.amazonaws.com/dev/bedrock_resource"

    # Model Selection
    GENERAL_PURPOSE_MODEL = BedrockModel.MISTRAL
    CODE_GENERATION_MODEL = BedrockModel.MISTRAL

    # API Keys (should be loaded from environment variables in production)
    MISTRAL_API_KEY = ""  # Add your Mistral API key
    LLAMA_API_KEY = ""    # Add your Llama API key
    CLAUDE_API_KEY = ""   # Add your Claude API key

    # Default model configurations
    DEFAULT_MAX_TOKENS = 512
    DEFAULT_TEMPERATURE = 0.5
    DEFAULT_TOP_P = 0.9
    DEFAULT_TOP_K = 50

    @classmethod
    def get_headers(cls, service: str) -> dict:
        """
        Get headers for the specified LLM service.
        
        Args:
            service (str): The LLM service name ('mistral', 'llama', or 'claude')
            
        Returns:
            dict: Headers for the API request
        """
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        if service == "mistral":
            headers["Authorization"] = f"Bearer {cls.MISTRAL_API_KEY}"
        elif service == "llama":
            headers["Authorization"] = f"Bearer {cls.LLAMA_API_KEY}"
        elif service == "claude":
            headers["x-api-key"] = cls.CLAUDE_API_KEY
            headers["anthropic-version"] = "2023-06-01"
            
        return headers 