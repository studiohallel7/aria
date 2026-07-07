"""
Quota Tracker - Tracks API usage and enforces quotas.
Supports daily and monthly limits with automatic resets.
"""

from datetime import datetime, timedelta
from typing import Optional
from dataclasses import dataclass


@dataclass
class QuotaStatus:
    """Current quota status."""
    daily_limit: float
    daily_used: float
    daily_remaining: float
    daily_usage_pct: float
    monthly_limit: float
    monthly_used: float
    monthly_remaining: float
    monthly_usage_pct: float
    next_daily_reset: datetime
    next_monthly_reset: datetime


class QuotaTracker:
    """Tracks and enforces API usage quotas."""
    
    def __init__(self, daily_limit: float = 0, monthly_limit: float = 0,
                 current_daily: float = 0, current_monthly: float = 0):
        self.daily_limit = daily_limit
        self.monthly_limit = monthly_limit
        self.daily_used = current_daily
        self.monthly_used = current_monthly
        
        # Reset times
        now = datetime.now()
        self.next_daily_reset = datetime(now.year, now.month, now.day) + timedelta(days=1)
        self.next_monthly_reset = datetime(now.year, now.month + 1, 1)
        
        # Check for resets on initialization
        self._check_resets()
    
    def _check_resets(self) -> None:
        """Check if quotas need to be reset."""
        now = datetime.now()
        
        if now >= self.next_daily_reset:
            self.daily_used = 0
            self.next_daily_reset = datetime(now.year, now.month, now.day) + timedelta(days=1)
        
        if now >= self.next_monthly_reset:
            self.monthly_used = 0
            if now.month == 12:
                self.next_monthly_reset = datetime(now.year + 1, 1, 1)
            else:
                self.next_monthly_reset = datetime(now.year, now.month + 1, 1)
    
    def record_usage(self, cost_usd: float) -> None:
        """Record usage against quotas."""
        self._check_resets()
        self.daily_used += cost_usd
        self.monthly_used += cost_usd
    
    def can_spend(self, amount: float) -> bool:
        """Check if a spend is within quota limits."""
        self._check_resets()
        
        if self.daily_limit > 0:
            if self.daily_used + amount > self.daily_limit:
                return False
        
        if self.monthly_limit > 0:
            if self.monthly_used + amount > self.monthly_limit:
                return False
        
        return True
    
    def get_status(self) -> QuotaStatus:
        """Get current quota status."""
        self._check_resets()
        
        daily_remaining = max(0, self.daily_limit - self.daily_used) if self.daily_limit > 0 else float('inf')
        monthly_remaining = max(0, self.monthly_limit - self.monthly_used) if self.monthly_limit > 0 else float('inf')
        
        daily_pct = (self.daily_used / self.daily_limit * 100) if self.daily_limit > 0 else 0
        monthly_pct = (self.monthly_used / self.monthly_limit * 100) if self.monthly_limit > 0 else 0
        
        return QuotaStatus(
            daily_limit=self.daily_limit,
            daily_used=self.daily_used,
            daily_remaining=daily_remaining,
            daily_usage_pct=daily_pct,
            monthly_limit=self.monthly_limit,
            monthly_used=self.monthly_used,
            monthly_remaining=monthly_remaining,
            monthly_usage_pct=monthly_pct,
            next_daily_reset=self.next_daily_reset,
            next_monthly_reset=self.next_monthly_reset,
        )
    
    def reset_daily(self) -> None:
        """Manually reset daily quota."""
        self.daily_used = 0
        now = datetime.now()
        self.next_daily_reset = datetime(now.year, now.month, now.day) + timedelta(days=1)
    
    def reset_monthly(self) -> None:
        """Manually reset monthly quota."""
        self.monthly_used = 0
        now = datetime.now()
        if now.month == 12:
            self.next_monthly_reset = datetime(now.year + 1, 1, 1)
        else:
            self.next_monthly_reset = datetime(now.year, now.month + 1, 1)