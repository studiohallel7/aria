"""
Intention Manager - Decides agent's next action intention.
Based on state, triggers, and user tasks.
"""

from typing import Dict, Any, Optional
from datetime import datetime


class IntentionManager:
    """Manages agent intentions and decision-making."""
    
    def __init__(self):
        self.priority_weights = {
            "user_task": 100,
            "error_recovery": 90,
            "explore": 30,
            "learn": 25,
            "reflect": 20,
            "none": 0,
        }
    
    def decide(
        self,
        state: Any,
        observations: Dict[str, Any],
        triggers: Dict[str, bool],
        has_user_tasks: bool,
    ) -> str:
        """Decide the next intention based on current context."""
        
        # User tasks always have highest priority
        if has_user_tasks:
            return "user_task"
        
        # Check for error recovery needs
        if observations.get("error_count", 0) > 5:
            return "error_recovery"
        
        # Mode-based decisions
        if state.mode.value == "livre":
            # In free mode, consider exploration and learning
            if triggers.get("curiosity", False):
                return "explore"
            if triggers.get("learning_opportunity", False):
                return "learn"
            if triggers.get("reflection_needed", False):
                return "reflect"
        
        # Default: no action needed
        return "none"
    
    def get_intention_description(self, intention: str) -> str:
        """Get human-readable description of an intention."""
        descriptions = {
            "user_task": "Executar tarefa do usuário",
            "error_recovery": "Recuperar de erro",
            "explore": "Explorar ativamente",
            "learn": "Aprender novo conhecimento",
            "reflect": "Refletir sobre ações",
            "none": "Aguardar próximos gatilhos",
        }
        return descriptions.get(intention, "Intenção desconhecida")