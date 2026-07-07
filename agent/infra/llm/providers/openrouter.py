"""
OpenRouter Provider implementation.
Supports multiple models from different providers via OpenRouter API.
"""

import os
import time
from typing import List, Dict, Any, Optional
import requests

from ..client import LLMProvider, LLMMessage, LLMResponse


class OpenRouterProvider(LLMProvider):
    """OpenRouter LLM provider - access to multiple models."""
    
    name = "openrouter"
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.base_url = base_url or "https://openrouter.ai/api/v1"
        
        # Model metadata for popular models on OpenRouter
        self._models = {
            "anthropic/claude-3.5-sonnet": {"purpose": "analise_codigo", "priority": 1},
            "google/gemini-pro-1.5": {"purpose": "contexto_longo", "priority": 2},
            "meta-llama/llama-3.1-70b-instruct": {"purpose": "custo_baixo", "priority": 3},
            "anthropic/claude-3-opus": {"purpose": "raciocinio_complexo", "priority": 1},
            "mistralai/mistral-large": {"purpose": "equilibrado", "priority": 2},
        }
    
    def chat_completion(
        self,
        messages: List[LLMMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
    ) -> LLMResponse:
        """Send a chat completion request to OpenRouter."""
        start_time = time.time()
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/autonomous-agent",
                "X-Title": "Autonomous Agent",
            }
            
            # Convert messages to OpenRouter format
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
            
            # Extract response
            content = data["choices"][0]["message"]["content"] or ""
            tokens_used = data.get("usage", {}).get("total_tokens", 0)
            
            # Estimate cost
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
        """Get list of configured OpenRouter models."""
        return [
            {"name": name, **metadata}
            for name, metadata in self._models.items()
        ]
    
    def _estimate_cost(self, model: str, tokens: int) -> float:
        """Estimate cost based on model and token count."""
        # Simplified pricing (per 1K tokens)
        pricing = {
            "anthropic/claude-3.5-sonnet": {"input": 0.003, "output": 0.015},
            "google/gemini-pro-1.5": {"input": 0.00025, "output": 0.0005},
            "meta-llama/llama-3.1-70b-instruct": {"input": 0.0008, "output": 0.0008},
            "anthropic/claude-3-opus": {"input": 0.015, "output": 0.075},
            "mistralai/mistral-large": {"input": 0.004, "output": 0.012},
        }
        
        rates = pricing.get(model, {"input": 0.001, "output": 0.002})
        input_tokens = int(tokens * 0.6)
        output_tokens = int(tokens * 0.4)
        
        return (input_tokens / 1000 * rates["input"]) + (output_tokens / 1000 * rates["output"])