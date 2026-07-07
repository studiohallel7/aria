"""
LLM Router - Intelligent routing for LLM requests.
Handles provider selection, load balancing, and failover.
"""

import yaml
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass, field
from enum import Enum

from .client import LLMProvider, LLMMessage, LLMResponse, BaseLLMClient, get_client
from .providers.openai import OpenAIProvider
from .providers.openrouter import OpenRouterProvider
from .providers.opencode import OpencodeProvider


class RoutingStrategy(Enum):
    """Routing strategy for selecting providers."""
    QUOTA_BASED = "quota_based"
    ROUND_ROBIN = "round_robin"
    LATENCY_BASED = "latency_based"
    PRIORITY_BASED = "priority_based"


@dataclass
class ProviderStatus:
    """Status of a provider."""
    name: str
    enabled: bool
    healthy: bool = True
    priority: int = 1
    last_error: Optional[str] = None
    last_error_time: Optional[datetime] = None
    consecutive_failures: int = 0
    avg_latency_ms: float = 0.0
    requests_count: int = 0
    cooldown_until: Optional[datetime] = None


@dataclass
class ModelInfo:
    """Information about a model."""
    name: str
    provider: str
    purpose: str
    max_tokens: int
    cost_per_1k_input: float
    cost_per_1k_output: float
    capabilities: List[str]
    priority: int


class LLMRouter:
    """Intelligent router for LLM requests."""
    
    def __init__(self, config_path: str = "./config/providers.yaml", 
                 accounts_config_path: str = "./config/accounts.yaml"):
        self.config_path = config_path
        self.accounts_config_path = accounts_config_path
        self.providers: Dict[str, LLMProvider] = {}
        self.provider_status: Dict[str, ProviderStatus] = {}
        self.models: Dict[str, ModelInfo] = {}
        self.routing_strategy: RoutingStrategy = RoutingStrategy.QUOTA_BASED
        self.fallback_chain: List[str] = []
        self.default_model: str = "gpt-4o-mini"
        
        # Load configurations
        self._load_configs()
        
        # Initialize providers
        self._initialize_providers()
        
        # Round-robin index
        self._rr_index = 0
    
    def _load_configs(self) -> None:
        """Load provider and accounts configurations."""
        try:
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f)
            
            with open(self.accounts_config_path, 'r') as f:
                self.accounts_config = yaml.safe_load(f)
            
            # Extract settings
            self.default_model = self.config.get('default_model', 'gpt-4o-mini')
            self.fallback_chain = self.config.get('fallback_chain', [])
            
            rotation_config = self.accounts_config.get('rotation', {})
            strategy_str = rotation_config.get('strategy', 'quota_based')
            self.routing_strategy = RoutingStrategy(strategy_str)
            
        except Exception as e:
            print(f"Warning: Could not load configs: {e}")
            self.config = {}
            self.accounts_config = {}
    
    def _initialize_providers(self) -> None:
        """Initialize all configured providers."""
        providers_config = self.config.get('providers', {})
        
        for provider_name, provider_cfg in providers_config.items():
            if not provider_cfg.get('enabled', False):
                continue
            
            try:
                provider = self._create_provider(provider_name, provider_cfg)
                if provider:
                    self.providers[provider_name] = provider
                    
                    # Get account config for this provider
                    account_cfg = self._get_primary_account(provider_name)
                    priority = account_cfg.get('priority', 1) if account_cfg else 1
                    
                    self.provider_status[provider_name] = ProviderStatus(
                        name=provider_name,
                        enabled=True,
                        priority=priority
                    )
                    
                    # Register models
                    for model_cfg in provider_cfg.get('models', []):
                        model_key = f"{provider_name}/{model_cfg['name']}"
                        self.models[model_key] = ModelInfo(
                            name=model_cfg['name'],
                            provider=provider_name,
                            purpose=model_cfg.get('purpose', 'general'),
                            max_tokens=model_cfg.get('max_tokens', 4096),
                            cost_per_1k_input=model_cfg.get('cost_per_1k_input', 0.001),
                            cost_per_1k_output=model_cfg.get('cost_per_1k_output', 0.002),
                            capabilities=model_cfg.get('capabilities', ['text']),
                            priority=model_cfg.get('priority', 1)
                        )
                        
            except Exception as e:
                print(f"Warning: Failed to initialize provider {provider_name}: {e}")
                self.provider_status[provider_name] = ProviderStatus(
                    name=provider_name,
                    enabled=False,
                    healthy=False,
                    last_error=str(e)
                )
    
    def _create_provider(self, name: str, config: Dict[str, Any]) -> Optional[LLMProvider]:
        """Create a provider instance based on name."""
        if name == 'openai':
            return OpenAIProvider(
                api_key=os.getenv("OPENAI_API_KEY"),
                base_url=config.get('base_url')
            )
        elif name == 'openrouter':
            return OpenRouterProvider(
                api_key=os.getenv("OPENROUTER_API_KEY"),
                base_url=config.get('base_url')
            )
        elif name == 'opencode':
            return OpencodeProvider(
                api_key=os.getenv("OPENCODE_API_KEY"),
                base_url=config.get('base_url')
            )
        return None
    
    def _get_primary_account(self, provider_name: str) -> Optional[Dict[str, Any]]:
        """Get primary account configuration for a provider."""
        accounts = self.accounts_config.get('accounts', {}).get(provider_name, [])
        for account in accounts:
            if account.get('enabled', False) and account.get('priority', 999) == 1:
                return account
        return accounts[0] if accounts else None
    
    def select_provider(self, purpose: str = "general", 
                       required_capabilities: List[str] = None) -> Optional[str]:
        """Select the best provider based on strategy and requirements."""
        available_providers = [
            (name, status) for name, status in self.provider_status.items()
            if status.enabled and status.healthy and 
            (status.cooldown_until is None or status.cooldown_until < datetime.now())
        ]
        
        if not available_providers:
            return None
        
        if self.routing_strategy == RoutingStrategy.ROUND_ROBIN:
            return self._select_round_robin(available_providers)
        elif self.routing_strategy == RoutingStrategy.LATENCY_BASED:
            return self._select_latency_based(available_providers)
        elif self.routing_strategy == RoutingStrategy.PRIORITY_BASED:
            return self._select_priority_based(available_providers, purpose, required_capabilities)
        else:  # QUOTA_BASED
            return self._select_quota_based(available_providers, purpose, required_capabilities)
    
    def _select_round_robin(self, providers: List[Tuple[str, ProviderStatus]]) -> str:
        """Select provider using round-robin."""
        self._rr_index = (self._rr_index + 1) % len(providers)
        return providers[self._rr_index][0]
    
    def _select_latency_based(self, providers: List[Tuple[str, ProviderStatus]]) -> str:
        """Select provider with lowest average latency."""
        return min(providers, key=lambda x: x[1].avg_latency_ms)[0]
    
    def _select_priority_based(self, providers: List[Tuple[str, ProviderStatus]], 
                               purpose: str, 
                               required_capabilities: List[str] = None) -> str:
        """Select provider based on priority and purpose matching."""
        # Filter by capabilities if required
        if required_capabilities:
            filtered = []
            for name, status in providers:
                provider_models = [m for m in self.models.values() if m.provider == name]
                has_capability = any(
                    any(cap in m.capabilities for cap in required_capabilities)
                    for m in provider_models
                )
                if has_capability:
                    filtered.append((name, status))
            if filtered:
                providers = filtered
        
        # Sort by priority
        sorted_providers = sorted(providers, key=lambda x: x[1].priority)
        return sorted_providers[0][0]
    
    def _select_quota_based(self, providers: List[Tuple[str, ProviderStatus]], 
                           purpose: str,
                           required_capabilities: List[str] = None) -> str:
        """Select provider based on quota availability and purpose."""
        # First, filter by capabilities if needed
        candidates = providers
        
        if required_capabilities:
            filtered = []
            for name, status in providers:
                provider_models = [m for m in self.models.values() if m.provider == name]
                has_capability = any(
                    any(cap in m.capabilities for cap in required_capabilities)
                    for m in provider_models
                )
                if has_capability:
                    filtered.append((name, status))
            if filtered:
                candidates = filtered
        
        # Check quota thresholds
        thresholds = self.accounts_config.get('thresholds', {})
        emergency_threshold = thresholds.get('emergency', 95)
        
        # Get providers with available quota
        quota_available = []
        for name, status in candidates:
            account = self._get_primary_account(name)
            if account:
                quota = account.get('quota', {})
                daily_limit = quota.get('daily_limit_usd', 0)
                daily_spent = quota.get('current_daily_spent', 0)
                
                if daily_limit > 0:
                    usage_pct = (daily_spent / daily_limit) * 100
                    if usage_pct < emergency_threshold:
                        quota_available.append((name, status, usage_pct))
                else:
                    quota_available.append((name, status, 0))
        
        if not quota_available:
            # Fallback to any available provider
            quota_available = [(name, status, 100) for name, status in candidates]
        
        # Sort by priority and quota usage
        sorted_candidates = sorted(quota_available, key=lambda x: (x[1].priority, x[2]))
        return sorted_candidates[0][0]
    
    def select_model(self, purpose: str = "general",
                    required_capabilities: List[str] = None,
                    max_budget: Optional[float] = None) -> Optional[str]:
        """Select the best model for the task."""
        candidates = []
        
        for model_key, model_info in self.models.items():
            # Check capabilities
            if required_capabilities:
                if not any(cap in model_info.capabilities for cap in required_capabilities):
                    continue
            
            # Check budget
            if max_budget is not None:
                estimated_cost = (model_info.cost_per_1k_input + model_info.cost_per_1k_output) / 1000
                if estimated_cost > max_budget:
                    continue
            
            # Check provider health
            provider_status = self.provider_status.get(model_info.provider)
            if not provider_status or not provider_status.healthy:
                continue
            
            candidates.append((model_key, model_info))
        
        if not candidates:
            return self.default_model
        
        # Sort by priority
        candidates.sort(key=lambda x: x[1].priority)
        return candidates[0][0]
    
    def chat_completion(self, messages: List[LLMMessage], 
                       model: Optional[str] = None,
                       temperature: float = 0.7,
                       max_tokens: Optional[int] = None,
                       purpose: str = "general",
                       required_capabilities: List[str] = None,
                       retry_on_failure: bool = True) -> LLMResponse:
        """Send a chat completion request with intelligent routing."""
        
        # Select model if not specified
        if model is None:
            model = self.select_model(purpose, required_capabilities)
        
        if model is None or '/' not in model:
            model = self.default_model
        
        # Parse provider and model name
        if '/' in model:
            provider_name, model_name = model.split('/', 1)
        else:
            provider_name = self._infer_provider(model)
            model_name = model
        
        # Attempt request with fallback chain
        attempted_providers = []
        last_error = None
        
        providers_to_try = [provider_name] + [
            p.split('/')[0] for p in self.fallback_chain if p.split('/')[0] != provider_name
        ]
        
        for provider_name in providers_to_try:
            if provider_name in attempted_providers:
                continue
            
            attempted_providers.append(provider_name)
            
            provider = self.providers.get(provider_name)
            if not provider:
                last_error = f"Provider {provider_name} not available"
                continue
            
            # Update status
            status = self.provider_status.get(provider_name)
            if status:
                status.requests_count += 1
            
            try:
                start_time = datetime.now()
                response = provider.chat_completion(
                    messages=messages,
                    model=model_name,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                
                # Update latency
                latency = (datetime.now() - start_time).total_seconds() * 1000
                if status:
                    # Moving average
                    n = status.requests_count
                    status.avg_latency_ms = ((n - 1) * status.avg_latency_ms + latency) / n
                
                if response.error:
                    last_error = response.error
                    if status:
                        status.consecutive_failures += 1
                        status.last_error = response.error
                        status.last_error_time = datetime.now()
                        
                        # Enter cooldown on multiple failures
                        if status.consecutive_failures >= 3:
                            cooldown_seconds = self.accounts_config.get('rotation', {}).get('cooldown_seconds', 300)
                            status.cooldown_until = datetime.now() + timedelta(seconds=cooldown_seconds)
                    continue
                
                # Success - reset failure counter
                if status:
                    status.consecutive_failures = 0
                    status.healthy = True
                
                return response
                
            except Exception as e:
                last_error = str(e)
                if status:
                    status.consecutive_failures += 1
                    status.last_error = str(e)
                    status.last_error_time = datetime.now()
        
        # All providers failed
        return LLMResponse(
            content="",
            model=model,
            provider=attempted_providers[0] if attempted_providers else "unknown",
            error=f"All providers failed. Last error: {last_error}",
        )
    
    def _infer_provider(self, model_name: str) -> str:
        """Infer provider from model name."""
        if model_name.startswith('gpt') or model_name.startswith('o1'):
            return 'openai'
        elif 'claude' in model_name or 'gemini' in model_name or 'llama' in model_name:
            return 'openrouter'
        else:
            return 'openai'  # default
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of all available models."""
        return [
            {
                'id': model_key,
                'name': model_info.name,
                'provider': model_info.provider,
                'purpose': model_info.purpose,
                'max_tokens': model_info.max_tokens,
                'capabilities': model_info.capabilities,
                'cost_per_1k_input': model_info.cost_per_1k_input,
                'cost_per_1k_output': model_info.cost_per_1k_output,
            }
            for model_key, model_info in self.models.items()
        ]
    
    def get_provider_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all providers."""
        return {
            name: {
                'enabled': status.enabled,
                'healthy': status.healthy,
                'priority': status.priority,
                'consecutive_failures': status.consecutive_failures,
                'avg_latency_ms': status.avg_latency_ms,
                'requests_count': status.requests_count,
                'last_error': status.last_error,
                'in_cooldown': status.cooldown_until and status.cooldown_until > datetime.now(),
            }
            for name, status in self.provider_status.items()
        }
    
    def mark_provider_unhealthy(self, provider_name: str, error: str) -> None:
        """Mark a provider as unhealthy."""
        if provider_name in self.provider_status:
            status = self.provider_status[provider_name]
            status.healthy = False
            status.last_error = error
            status.last_error_time = datetime.now()
            status.consecutive_failures += 1
    
    def mark_provider_healthy(self, provider_name: str) -> None:
        """Mark a provider as healthy."""
        if provider_name in self.provider_status:
            status = self.provider_status[provider_name]
            status.healthy = True
            status.consecutive_failures = 0
            status.last_error = None


# Global router instance
_router: Optional[LLMRouter] = None


def get_router() -> LLMRouter:
    """Get or create the global LLM router."""
    global _router
    if _router is None:
        _router = LLMRouter()
    return _router


def reset_router() -> None:
    """Reset the global router (for testing)."""
    global _router
    _router = None