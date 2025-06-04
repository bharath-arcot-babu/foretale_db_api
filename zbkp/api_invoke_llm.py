import json
import requests
from typing import Dict, Any, Optional
from enum import Enum
from ..layer_llm_service.config_llm_api import LLMApiConfig

class LLMModel(Enum):
    MISTRAL = "mistral"
    LLAMA3 = "llama3"
    CLAUDE3 = "claude3"

class LlmModelPicker:
    def __init__(self):
        self.general_purpose_llm = LLMModel.MISTRAL
        self.code_generation_llm = LLMModel.MISTRAL

class LLMService:
    def __init__(self):
        self.model_picker = LlmModelPicker()
        self.model = self.model_picker.general_purpose_llm

    def call_llm_general_purpose(
        self,
        prompt: str,
        max_tokens: int = 512,
        temperature: float = 0.5,
        top_p: float = 0.9,
        top_k: int = 50
    ) -> Dict[str, Any]:
        selected_model = self.model_picker.general_purpose_llm
        if selected_model == LLMModel.MISTRAL:
            return self._call_mistral(prompt, max_tokens, temperature, top_p, top_k)
        elif selected_model == LLMModel.LLAMA3:
            return self._call_llama3(prompt, max_tokens, temperature, top_p)
        elif selected_model == LLMModel.CLAUDE3:
            return self._call_claude3(prompt, max_tokens, temperature, top_p, top_k)

    def call_llm_for_code_generation(
        self,
        prompt: str,
        max_tokens: int = 512,
        temperature: float = 0.5,
        top_p: float = 0.9,
        top_k: int = 50
    ) -> Dict[str, Any]:
        selected_model = self.model_picker.code_generation_llm
        if selected_model == LLMModel.MISTRAL:
            return self._call_mistral(prompt, max_tokens, temperature, top_p, top_k)
        elif selected_model == LLMModel.LLAMA3:
            return self._call_llama3(prompt, max_tokens, temperature, top_p)
        elif selected_model == LLMModel.CLAUDE3:
            return self._call_claude3(prompt, max_tokens, temperature, top_p, top_k)

    @staticmethod
    def _call_mistral(
        prompt: str,
        max_tokens: int,
        temperature: float,
        top_p: float,
        top_k: int
    ) -> Dict[str, Any]:
        url = LLMApiConfig.BASE_MISTRAL_URL

        body = {
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "top_k": top_k,
            "system_instruction": ""
        }

        response = requests.post(
            url,
            headers=LLMApiConfig.get_headers("mistral"),
            json=body
        )
        
        outer = response.json()
        inner_json_body = json.loads(outer['body'])
        return json.loads(inner_json_body['model_response'])

    @staticmethod
    def _call_llama3(
        prompt: str,
        max_gen_len: int,
        temperature: float,
        top_p: float
    ) -> Dict[str, Any]:
        url = LLMApiConfig.BASE_LLAMA_URL

        body = {
            "prompt": prompt,
            "max_gen_len": max_gen_len,
            "temperature": temperature,
            "top_p": top_p
        }

        response = requests.post(
            url,
            headers=LLMApiConfig.get_headers("llama"),
            json=body
        )

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"LLaMA 3 Error: {response.status_code}, {response.text}")

    @staticmethod
    def _call_claude3(
        user_message: str,
        max_tokens: int,
        temperature: float,
        top_p: float,
        top_k: int
    ) -> Dict[str, Any]:
        url = LLMApiConfig.BASE_CLAUDE_URL

        body = {
            "modelId": "anthropic.claude-3-5-sonnet-20241022-v2:0",
            "contentType": "application/json",
            "accept": "application/json",
            "body": {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": max_tokens,
                "top_k": top_k,
                "stop_sequences": [],
                "temperature": temperature,
                "top_p": top_p,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": user_message}
                        ]
                    }
                ]
            }
        }

        response = requests.post(
            url,
            headers=LLMApiConfig.get_headers("claude"),
            json=body
        )

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Claude 3 Error: {response.status_code}, {response.text}")

    @staticmethod
    def _get_headers() -> Dict[str, str]:
        return {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
