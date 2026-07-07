"""
Context manager module - re-exports from agent_state for backwards compatibility.
"""

from .agent_state import (
    ContextManager,
    ContextItem,
    StatePersistence,
    get_context_manager,
    save_context_manager,
)

__all__ = [
    "ContextManager",
    "ContextItem", 
    "StatePersistence",
    "get_context_manager",
    "save_context_manager",
]