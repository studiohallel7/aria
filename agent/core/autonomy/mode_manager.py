"""
Mode Manager - Handles agent operation mode transitions.
Manages trabalho (work) vs livre (free) modes.
"""

from typing import Dict, Any, Optional
from datetime import datetime

from core.state.agent_state import OperationMode


class ModeManager:
    """Manages agent operation modes and transitions."""
    
    def __init__(self):
        self.current_mode = OperationMode.TRABALHO
        self.mode_history: list = []
        self.last_transition: Optional[datetime] = None
    
    def get_mode(self) -> OperationMode:
        """Get current operation mode."""
        return self.current_mode
    
    def set_mode(self, mode: OperationMode, reason: str = "manual") -> None:
        """Set operation mode with history tracking."""
        if self.current_mode != mode:
            self.mode_history.append({
                "from": self.current_mode.value,
                "to": mode.value,
                "reason": reason,
                "timestamp": datetime.now().isoformat(),
            })
            self.current_mode = mode
            self.last_transition = datetime.now()
    
    def should_switch_to_free(self, conditions: Dict[str, Any]) -> bool:
        """Evaluate if agent should switch to free mode."""
        # Conditions for switching to free mode
        if conditions.get("no_user_tasks", False):
            if conditions.get("idle_time_seconds", 0) > 300:  # 5 minutes
                return True
        
        return False
    
    def should_switch_to_work(self, conditions: Dict[str, Any]) -> bool:
        """Evaluate if agent should switch to work mode."""
        # User task always triggers work mode
        if conditions.get("user_task_received", False):
            return True
        
        # High priority external event
        if conditions.get("high_priority_event", False):
            return True
        
        return False
    
    def evaluate_transition(self, context: Dict[str, Any]) -> Optional[OperationMode]:
        """Evaluate if a mode transition is needed."""
        if self.current_mode == OperationMode.TRABALHO:
            if self.should_switch_to_free(context):
                return OperationMode.LIVRE
        else:
            if self.should_switch_to_work(context):
                return OperationMode.TRABALHO
        
        return None
    
    def get_mode_description(self) -> str:
        """Get human-readable mode description."""
        descriptions = {
            OperationMode.TRABALHO: "Modo Trabalho - Seguindo tarefas do usuário",
            OperationMode.LIVRE: "Modo Livre - Exploração e aprendizado autônomo",
        }
        return descriptions.get(self.current_mode, "Modo desconhecido")