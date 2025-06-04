"""
Utility functions for invoking AWS Bedrock models through LangChain.
"""

import json
from typing import Dict, Any, Union
import boto3
from .config_llm_api import LLMApiConfig, BedrockModel
from langchain_aws import ChatBedrock
from langchain_core.messages import AIMessage

class BedrockLangChainService:
    def __init__(self):
        self.model = LLMApiConfig.GENERAL_PURPOSE_MODEL
        try:
            # Initialize the Bedrock client
            self.bedrock_client = boto3.client(
                service_name="bedrock-runtime",
                region_name=LLMApiConfig.AWS_REGION
            )

            # Initialize the LLM model
            self.llm = self._initialize_llm()

        except Exception as e:
            raise RuntimeError(f"Failed to initialize Bedrock client: {str(e)}")

    def _initialize_llm(self) -> ChatBedrock:
        """Initialize the Bedrock LLM model with default parameters based on the configured model."""
        selected_model = LLMApiConfig.GENERAL_PURPOSE_MODEL
        
        # Initialize the LLM model based on the selected model
        if selected_model == BedrockModel.MISTRAL:
            # Initialize the Mistral model
            return ChatBedrock(
                client=self.bedrock_client,
                verbose=False,
                model_id=BedrockModel.MISTRAL.value,
                model_kwargs={
                    "max_tokens": LLMApiConfig.DEFAULT_MAX_TOKENS,
                    "temperature": LLMApiConfig.DEFAULT_TEMPERATURE,
                    "top_p": LLMApiConfig.DEFAULT_TOP_P,
                    "top_k": LLMApiConfig.DEFAULT_TOP_K
                }
            )
        else:
            raise ValueError(f"Unsupported model type: {selected_model}")

    def get_llm(self) -> ChatBedrock:
        """Get the initialized LLM model for reuse."""
        return self.llm

    def call_llm_general_purpose(
        self,
        prompt: str,
        max_tokens: int = LLMApiConfig.DEFAULT_MAX_TOKENS,
        temperature: float = LLMApiConfig.DEFAULT_TEMPERATURE,
        top_p: float = LLMApiConfig.DEFAULT_TOP_P,
        top_k: int = LLMApiConfig.DEFAULT_TOP_K
    ) -> Dict[str, Any]:
        
        selected_model = LLMApiConfig.GENERAL_PURPOSE_MODEL
        if selected_model == BedrockModel.MISTRAL:
            return self._call_mistral(prompt, max_tokens, temperature, top_p, top_k)

    def call_llm_for_code_generation(
        self,
        prompt: str,
        max_tokens: int = LLMApiConfig.DEFAULT_MAX_TOKENS,
        temperature: float = LLMApiConfig.DEFAULT_TEMPERATURE,
        top_p: float = LLMApiConfig.DEFAULT_TOP_P,
        top_k: int = LLMApiConfig.DEFAULT_TOP_K
    ) -> Dict[str, Any]:
        
        selected_model = LLMApiConfig.CODE_GENERATION_MODEL
        if selected_model == BedrockModel.MISTRAL:
            return self._call_mistral(prompt, max_tokens, temperature, top_p, top_k)

    def _call_mistral(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float,
        top_p: float,
        top_k: int
    ) -> Dict[str, Any]:
        # Use the initialized LLM model
        response = self.llm.invoke(prompt)
        return self._parse_response(response)

    @staticmethod
    def _parse_response(response: Union[AIMessage, str]) -> Dict[str, Any]:
        try:
            if isinstance(response, AIMessage):
                content = response.content.strip()
            elif isinstance(response, str):
                content = response.strip()
            else:
                return {"error": "Unsupported response type", "type": str(type(response))}
            
            return json.loads(content)
        except Exception as e:
            return {"error": str(e), "raw_content": response.content if isinstance(response, AIMessage) else response}