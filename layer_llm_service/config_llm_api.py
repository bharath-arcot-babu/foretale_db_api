"""
Configuration file for LLM API endpoints and settings.
"""

from enum import Enum

class BedrockModel(Enum):
    MISTRAL = "mistral.mistral-large-2402-v1:0"

class LLMApiConfig:
    # AWS Region
    AWS_REGION = "us-east-1"

    # Model Selection
    GENERAL_PURPOSE_MODEL = BedrockModel.MISTRAL
    CODE_GENERATION_MODEL = BedrockModel.MISTRAL

    # API Keys (should be loaded from environment variables in production)
    MISTRAL_API_KEY = ""  # Add your Mistral API key

    # Default MISTRAL model configurations
    DEFAULT_MAX_TOKENS = 1000
    DEFAULT_TEMPERATURE = 0.5
    DEFAULT_TOP_P = 0.9
    DEFAULT_TOP_K = 50