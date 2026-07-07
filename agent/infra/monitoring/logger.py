"""
Agent Logger - Unified logging system.
Handles logs with different levels and persistence.
"""

import os
import logging
from datetime import datetime
from typing import Optional


class AgentLogger:
    """Unified logger for the autonomous agent."""
    
    def __init__(self, log_path: str = "./data/agent/logs", level: str = "INFO"):
        self.log_path = log_path
        os.makedirs(log_path, exist_ok=True)
        
        # Setup logging
        self.logger = logging.getLogger("autonomous_agent")
        self.logger.setLevel(getattr(logging, level.upper()))
        
        # Clear existing handlers
        self.logger.handlers = []
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_format)
        self.logger.addHandler(console_handler)
        
        # File handler (daily rotation)
        today = datetime.now().strftime("%Y-%m-%d")
        file_path = os.path.join(log_path, f"agent_{today}.log")
        file_handler = logging.FileHandler(file_path)
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(file_format)
        self.logger.addHandler(file_handler)
    
    def debug(self, message: str) -> None:
        """Log debug message."""
        self.logger.debug(message)
    
    def info(self, message: str) -> None:
        """Log info message."""
        self.logger.info(message)
    
    def warning(self, message: str) -> None:
        """Log warning message."""
        self.logger.warning(message)
    
    def error(self, message: str) -> None:
        """Log error message."""
        self.logger.error(message)
    
    def critical(self, message: str) -> None:
        """Log critical message."""
        self.logger.critical(message)
    
    def log_action(self, action: str, result: str, details: Optional[dict] = None) -> None:
        """Log an agent action."""
        message = f"ACTION: {action} -> {result}"
        if details:
            message += f" | {details}"
        self.info(message)
    
    def log_cycle(self, cycle_num: int, intention: str, duration_ms: float) -> None:
        """Log a cycle completion."""
        self.debug(f"Cycle {cycle_num}: intention={intention}, duration={duration_ms:.2f}ms")