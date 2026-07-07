"""
OpenAI Provider implementation.
"""

import os
import time
from typing import List, Dict, Any, Optional
from datetime import datetime

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from ..client import LLMProvider, LLMMessage, LLMResponse


class OpenAIProvider(LLMProvider):
    """OpenAI LLM provider."""
    
    name = "openai"
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = base_url or "https://api.openai.com/v1"
        
        if not OPENAI_AVAILABLE:
            raise ImportError("openai package not installed. Run: pip install openai")
        
        self._client = openai.OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
        )
        
        # Model metadata
        self._models = {
            "gpt-4o": {"purpose": "raciocinio_complexo", "priority": 1},
            "gpt-4o-mini": {"purpose": "tarefas_rapidas", "priority": 2},
            "o1-preview": {"purpose": "raciocinio_profundo", "priority": 3},
        }
    
    def chat_completion(
        self,
        messages: List[LLMMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
    ) -> LLMResponse:
        """Send a chat completion request to OpenAI."""
        start_time = time.time()
        
        try:
            # Convert messages to OpenAI format
            formatted_messages = [msg.to_dict() for msg in messages]
            
            # Handle o1 models differently (no temperature, different params)
            if model.startswith("o1"):
                response = self._client.chat.completions.create(
                    model=model,
                    messages=formatted_messages,
                    max_tokens=max_tokens,
                )
            else:
                response = self._client.chat.completions.create(
                    model=model,
                    messages=formatted_messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            content = response.choices[0].message.content or ""
            tokens_used = response.usage.total_tokens if response.usage else 0
            
            # Estimate cost (simplified)
            cost_usd = self._estimate_cost(model, tokens_used)
            
            return LLMResponse(
                content=content,
                model=model,
                provider=self.name,
                tokens_used=tokens_used,
                latency_ms=latency_ms,
                cost_usd=cost_usd,
                raw_response=response.model_dump(),
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
        """Get list of available OpenAI models."""
        return [
            {"name": name, **metadata}
            for name, metadata in self._models.items()
        ]
    
    def _estimate_cost(self, model: str, tokens: int) -> float:
        """Estimate cost based on model and token count."""
        # Simplified pricing (per 1K tokens)
        pricing = {
            "gpt-4o": {"input": 0.005, "output": 0.015},
            "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
            "o1-preview": {"input": 0.015, "output": 0.06},
        }
        
        rates = pricing.get(model, {"input": 0.001, "output": 0.002})
        # Rough estimate: assume 60% input, 40% output
        input_tokens = int(tokens * 0.6)
        output_tokens = int(tokens * 0.4)
        
        return (input_tokens / 1000 * rates["input"]) + (output_tokens / 1000 * rates["output"])