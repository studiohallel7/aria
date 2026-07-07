"""
Trigger Evaluator - Evaluates conditions that trigger agent actions.
Handles time-based, event-based, and curiosity-based triggers.
"""

import random
from typing import Dict, Any, List
from datetime import datetime


class TriggerEvaluator:
    """Evaluates triggers for agent actions."""
    
    def __init__(self, curiosity_threshold: float = 0.3):
        self.curiosity_threshold = curiosity_threshold
        self.trigger_history: List[Dict[str, Any]] = []
    
    def evaluate(
        self,
        observations: Dict[str, Any],
        pending_tasks: List[Dict],
        state: Any,
    ) -> Dict[str, bool]:
        """Evaluate all triggers and return active ones."""
        triggers = {
            "time_based": self._check_time_trigger(),
            "curiosity": self._check_curiosity_trigger(state, observations),
            "learning_opportunity": self._check_learning_trigger(observations),
            "reflection_needed": self._check_reflection_trigger(observations),
            "error_recovery": self._check_error_trigger(observations),
            "external_event": False,  # Would be set by external systems
        }
        
        # Record trigger evaluation
        self.trigger_history.append({
            "timestamp": datetime.now().isoformat(),
            "active_triggers": [k for k, v in triggers.items() if v],
        })
        
        return triggers
    
    def _check_time_trigger(self) -> bool:
        """Check if time-based trigger is active."""
        # Simple implementation: trigger every N cycles
        # In production, would use configurable intervals
        return False
    
    def _check_curiosity_trigger(self, state: Any, observations: Dict) -> bool:
        """Check if curiosity trigger should fire."""
        # Only in free mode
        if state.mode.value != "livre":
            return False
        
        # Random chance based on threshold
        if random.random() < self.curiosity_threshold:
            return True
        
        return False
    
    def _check_learning_trigger(self, observations: Dict) -> bool:
        """Check if learning opportunity exists."""
        # Would analyze context for learning opportunities
        # Simplified: check if there's new information
        return False
    
    def _check_reflection_trigger(self, observations: Dict) -> bool:
        """Check if reflection is needed."""
        # Trigger reflection after many actions or errors
        error_count = observations.get("error_count", 0)
        if error_count > 3:
            return True
        
        return False
    
    def _check_error_trigger(self, observations: Dict) -> bool:
        """Check if error recovery is needed."""
        error_count = observations.get("error_count", 0)
        return error_count > 5
    
    def register_external_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Register an external event trigger."""
        self.trigger_history.append({
            "timestamp": datetime.now().isoformat(),
            "type": "external",
            "event_type": event_type,
            "data": data,
        })
    
    def get_recent_triggers(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent trigger evaluations."""
        return self.trigger_history[-limit:]