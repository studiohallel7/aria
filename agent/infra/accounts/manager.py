"""
Accounts Manager - Manages API keys and account rotation.
Handles multiple accounts per provider with automatic failover.
"""

import yaml
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from enum import Enum

from .quota_tracker import QuotaTracker, QuotaStatus
from .healthcheck import HealthChecker


@dataclass
class Account:
    """Represents an API account."""
    id: str
    provider: str
    api_key: str
    enabled: bool = True
    priority: int = 1
    quota: Optional[QuotaTracker] = None
    last_used: Optional[datetime] = None
    consecutive_failures: int = 0
    cooldown_until: Optional[datetime] = None


class RotationStrategy(Enum):
    """Strategy for rotating between accounts."""
    QUOTA_BASED = "quota_based"
    ROUND_ROBIN = "round_robin"
    LATENCY_BASED = "latency_based"
    PRIORITY_BASED = "priority_based"


class AccountsManager:
    """Manages multiple API accounts across providers."""
    
    def __init__(self, config_path: str = "./config/accounts.yaml"):
        self.config_path = config_path
        self.accounts: Dict[str, List[Account]] = {}  # provider -> list of accounts
        self.rotation_strategy: RotationStrategy = RotationStrategy.QUOTA_BASED
        self.health_checker: Optional[HealthChecker] = None
        self.cooldown_seconds: int = 300
        self._rr_index: Dict[str, int] = {}  # round-robin index per provider
        
        self._load_config()
        self._initialize_accounts()
    
    def _load_config(self) -> None:
        """Load accounts configuration."""
        try:
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f)
            
            rotation_config = self.config.get('rotation', {})
            strategy_str = rotation_config.get('strategy', 'quota_based')
            self.rotation_strategy = RotationStrategy(strategy_str)
            self.cooldown_seconds = rotation_config.get('cooldown_seconds', 300)
            
            # Initialize health checker
            health_interval = rotation_config.get('health_check_interval', 60)
            self.health_checker = HealthChecker(check_interval=health_interval)
            
        except Exception as e:
            print(f"Warning: Could not load accounts config: {e}")
            self.config = {}
    
    def _initialize_accounts(self) -> None:
        """Initialize all configured accounts."""
        accounts_config = self.config.get('accounts', {})
        
        for provider, provider_accounts in accounts_config.items():
            self.accounts[provider] = []
            self._rr_index[provider] = 0
            
            for acc_cfg in provider_accounts:
                if not acc_cfg.get('enabled', False):
                    continue
                
                # Get API key from environment
                api_key_env = acc_cfg.get('api_key_env')
                api_key = os.getenv(api_key_env) if api_key_env else None
                
                if not api_key:
                    print(f"Warning: API key not found for {provider}/{acc_cfg['id']}")
                    continue
                
                # Create quota tracker
                quota_cfg = acc_cfg.get('quota', {})
                quota = QuotaTracker(
                    daily_limit=quota_cfg.get('daily_limit_usd', 0),
                    monthly_limit=quota_cfg.get('monthly_limit_usd', 0),
                    current_daily=quota_cfg.get('current_daily_spent', 0),
                    current_monthly=quota_cfg.get('current_monthly_spent', 0),
                )
                
                account = Account(
                    id=acc_cfg['id'],
                    provider=provider,
                    api_key=api_key,
                    enabled=True,
                    priority=acc_cfg.get('priority', 1),
                    quota=quota,
                )
                
                self.accounts[provider].append(account)
            
            # Sort by priority
            self.accounts[provider].sort(key=lambda x: x.priority)
    
    def get_account(self, provider: str, 
                   strategy: Optional[RotationStrategy] = None) -> Optional[Account]:
        """Get the best account for a provider based on strategy."""
        if provider not in self.accounts or not self.accounts[provider]:
            return None
        
        available_accounts = [
            acc for acc in self.accounts[provider]
            if acc.enabled and 
            (acc.cooldown_until is None or acc.cooldown_until < datetime.now())
        ]
        
        if not available_accounts:
            return None
        
        strat = strategy or self.rotation_strategy
        
        if strat == RotationStrategy.ROUND_ROBIN:
            return self._select_round_robin(provider, available_accounts)
        elif strat == RotationStrategy.PRIORITY_BASED:
            return self._select_priority(available_accounts)
        elif strat == RotationStrategy.QUOTA_BASED:
            return self._select_quota_based(available_accounts)
        else:
            return available_accounts[0]
    
    def _select_round_robin(self, provider: str, 
                           accounts: List[Account]) -> Account:
        """Select account using round-robin."""
        idx = self._rr_index[provider]
        account = accounts[idx % len(accounts)]
        self._rr_index[provider] = (idx + 1) % len(accounts)
        return account
    
    def _select_priority(self, accounts: List[Account]) -> Account:
        """Select account with highest priority (lowest number)."""
        return min(accounts, key=lambda x: x.priority)
    
    def _select_quota_based(self, accounts: List[Account]) -> Account:
        """Select account with best quota availability."""
        thresholds = self.config.get('thresholds', {})
        emergency_threshold = thresholds.get('emergency', 95)
        
        candidates = []
        for acc in accounts:
            if acc.quota:
                status = acc.quota.get_status()
                if status.daily_usage_pct < emergency_threshold:
                    candidates.append((acc, status.daily_usage_pct))
            else:
                candidates.append((acc, 0))
        
        if not candidates:
            # Fallback to any available account
            candidates = [(acc, 100) for acc in accounts]
        
        # Sort by quota usage
        candidates.sort(key=lambda x: x[1])
        return candidates[0][0]
    
    def record_usage(self, account: Account, cost_usd: float) -> None:
        """Record usage for an account."""
        if account.quota:
            account.quota.record_usage(cost_usd)
        account.last_used = datetime.now()
    
    def record_failure(self, account: Account) -> None:
        """Record a failure for an account."""
        account.consecutive_failures += 1
        
        # Enter cooldown after multiple failures
        if account.consecutive_failures >= 3:
            account.cooldown_until = datetime.now() + timedelta(seconds=self.cooldown_seconds)
    
    def record_success(self, account: Account) -> None:
        """Record a success for an account."""
        account.consecutive_failures = 0
        account.cooldown_until = None
    
    def get_all_accounts(self) -> List[Dict[str, Any]]:
        """Get information about all accounts."""
        result = []
        for provider, accounts in self.accounts.items():
            for acc in accounts:
                quota_status = acc.quota.get_status() if acc.quota else None
                result.append({
                    'provider': provider,
                    'id': acc.id,
                    'enabled': acc.enabled,
                    'priority': acc.priority,
                    'last_used': acc.last_used.isoformat() if acc.last_used else None,
                    'consecutive_failures': acc.consecutive_failures,
                    'in_cooldown': acc.cooldown_until and acc.cooldown_until > datetime.now(),
                    'quota_status': {
                        'daily_usage_pct': quota_status.daily_usage_pct if quota_status else 0,
                        'monthly_usage_pct': quota_status.monthly_usage_pct if quota_status else 0,
                        'daily_remaining': quota_status.daily_remaining if quota_status else 0,
                        'monthly_remaining': quota_status.monthly_remaining if quota_status else 0,
                    } if quota_status else None,
                })
        return result
    
    def add_account(self, provider: str, account_id: str, api_key: str,
                   priority: int = 1, quota_config: Optional[Dict] = None) -> Account:
        """Add a new account."""
        quota = None
        if quota_config:
            quota = QuotaTracker(
                daily_limit=quota_config.get('daily_limit_usd', 0),
                monthly_limit=quota_config.get('monthly_limit_usd', 0),
            )
        
        account = Account(
            id=account_id,
            provider=provider,
            api_key=api_key,
            enabled=True,
            priority=priority,
            quota=quota,
        )
        
        if provider not in self.accounts:
            self.accounts[provider] = []
            self._rr_index[provider] = 0
        
        self.accounts[provider].append(account)
        self.accounts[provider].sort(key=lambda x: x.priority)
        
        return account
    
    def disable_account(self, provider: str, account_id: str) -> bool:
        """Disable an account."""
        if provider not in self.accounts:
            return False
        
        for acc in self.accounts[provider]:
            if acc.id == account_id:
                acc.enabled = False
                return True
        return False
    
    def enable_account(self, provider: str, account_id: str) -> bool:
        """Enable an account."""
        if provider not in self.accounts:
            return False
        
        for acc in self.accounts[provider]:
            if acc.id == account_id:
                acc.enabled = True
                return True
        return False


# Global manager instance
_manager: Optional[AccountsManager] = None


def get_manager() -> AccountsManager:
    """Get or create the global accounts manager."""
    global _manager
    if _manager is None:
        _manager = AccountsManager()
    return _manager


def reset_manager() -> None:
    """Reset the global manager (for testing)."""
    global _manager
    _manager = None