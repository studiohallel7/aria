"""
Opencode Provider implementation.
"""

import os
import time
from typing import List, Dict, Any, Optional
import requests

from ..client import LLMProvider, LLMMessage, LLMResponse


class OpencodeProvider(LLMProvider):
    """Opencode LLM provider - Suporte para DeepSeek V4 Flash Free e GPT-5.5."""
    
    name = "opencode"
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENCODE_API_KEY", "")
        # URL correta conforme documentação
        self.base_url = base_url or "https://opencode.ai/zen/v1/chat/completions"
        
        # Model metadata - modelos disponíveis no OpenCode
        self._models = {
            "deepseek-v4-flash-free": {"purpose": "code", "priority": 1},
            "gpt-5.5": {"purpose": "general", "priority": 2},
        }
    
    def chat_completion(
        self,
        messages: List[LLMMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
    ) -> LLMResponse:
        """Send a chat completion request to Opencode."""
        start_time = time.time()
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            
            formatted_messages = [msg.to_dict() for msg in messages]
            
            payload = {
                "model": model,
                "messages": formatted_messages,
                "temperature": temperature,
            }
            
            if max_tokens:
                payload["max_tokens"] = max_tokens
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=60,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            if response.status_code != 200:
                return LLMResponse(
                    content="",
                    model=model,
                    provider=self.name,
                    latency_ms=latency_ms,
                    error=f"HTTP {response.status_code}: {response.text}",
                )
            
            data = response.json()
            content = data["choices"][0]["message"]["content"] or ""
            tokens_used = data.get("usage", {}).get("total_tokens", 0)
            cost_usd = self._estimate_cost(model, tokens_used)
            
            return LLMResponse(
                content=content,
                model=model,
                provider=self.name,
                tokens_used=tokens_used,
                latency_ms=latency_ms,
                cost_usd=cost_usd,
                raw_response=data,
            )
            
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            return LLMResponse(
                content="",
                model=model,
                provider=self.name,
                latency_ms=latency_ms,
                error=str(e),
            )
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of configured Opencode models."""
        return [
            {"name": name, **metadata}
            for name, metadata in self._models.items()
        ]
    
    def _estimate_cost(self, model: str, tokens: int) -> float:
        """Estimate cost based on model and token count.
        
        OpenCode oferece modelos gratuitos, então o custo é zero.
        """
        # Modelos OpenCode são gratuitos
        return 0.0