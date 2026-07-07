"""
LLM Client - Unified interface for all LLM providers.
Handles authentication, request formatting, and response parsing.
"""

import os
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Generator
from datetime import datetime
import json


@dataclass
class LLMMessage:
    """A message in a conversation."""
    role: str  # system, user, assistant
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, str]:
        return {"role": self.role, "content": self.content}


@dataclass
class LLMResponse:
    """Response from an LLM call."""
    content: str
    model: str
    provider: str
    tokens_used: int = 0
    latency_ms: float = 0.0
    cost_usd: float = 0.0
    raw_response: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "model": self.model,
            "provider": self.provider,
            "tokens_used": self.tokens_used,
            "latency_ms": self.latency_ms,
            "cost_usd": self.cost_usd,
            "error": self.error,
        }


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    name: str = "base"
    
    @abstractmethod
    def chat_completion(
        self,
        messages: List[LLMMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
    ) -> LLMResponse:
        """Send a chat completion request."""
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available models for this provider."""
        pass


class BaseLLMClient:
    """Base client with common functionality."""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key
        self.base_url = base_url
        self._providers: Dict[str, LLMProvider] = {}
        
    def register_provider(self, provider: LLMProvider) -> None:
        """Register an LLM provider."""
        self._providers[provider.name] = provider
        
    def get_provider(self, name: str) -> Optional[LLMProvider]:
        """Get a registered provider by name."""
        return self._providers.get(name)
    
    def list_providers(self) -> List[str]:
        """List all registered providers."""
        return list(self._providers.keys())


# Global client instance
_client: Optional[BaseLLMClient] = None


def get_client() -> BaseLLMClient:
    """Get or create the global LLM client."""
    global _client
    if _client is None:
        _client = BaseLLMClient()
    return _client


def reset_client() -> None:
    """Reset the global client (for testing)."""
    global _client
    _client = None