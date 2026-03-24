from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Protocol

import requests

@dataclass
class LLMResponse:
    content: str
    provider: str

class LLMProvider(Protocol):
    def complete(self, prompt: str) -> LLMResponse: ...

class OpenAICompatibleProvider:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY', '')
        self.base_url = os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')
        self.model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')

    def complete(self, prompt: str) -> LLMResponse:
        response = requests.post(
            f'{self.base_url}/chat/completions',
            headers={'Authorization': f'Bearer {self.api_key}', 'Content-Type': 'application/json'},
            json={
                'model': self.model,
                'messages': [{'role': 'system', 'content': prompt}],
                'temperature': 0.2,
            },
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        return LLMResponse(content=data['choices'][0]['message']['content'], provider=self.model)

class RuleBasedProvider:
    def complete(self, prompt: str) -> LLMResponse:
        return LLMResponse(content=prompt[:500], provider='rule-based')


def get_llm_provider() -> LLMProvider:
    if os.getenv('OPENAI_API_KEY'):
        return OpenAICompatibleProvider()
    return RuleBasedProvider()
