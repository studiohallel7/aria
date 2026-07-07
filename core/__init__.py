"""Core - Núcleo cognitivo do agente"""

from core.state.agent_state import StateManager, AgentState, AgentMode, Task
from core.state.context_manager import ContextManager
from core.cognition.intention import IntentionEngine, IntentionType
from core.cognition.thinking import ThinkingEngine
from core.cognition.planner import Planner
from core.cognition.reflection import ReflectionEngine
from core.autonomy.mode_manager import ModeManager, Mode
from core.autonomy.priorities import PriorityManager
from core.autonomy.triggers import TriggerManager
from core.loop.main_loop import AgentLoop

__all__ = [
    # Estado
    "StateManager",
    "AgentState",
    "AgentMode",
    "Task",
    "ContextManager",
    
    # Cognição
    "IntentionEngine",
    "IntentionType",
    "ThinkingEngine",
    "Planner",
    "ReflectionEngine",
    
    # Autonomia
    "ModeManager",
    "Mode",
    "PriorityManager",
    "TriggerManager",
    
    # Loop
    "AgentLoop"
]