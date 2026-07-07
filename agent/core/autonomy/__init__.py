"""
Módulo de Autonomia do Agente.

Inclui:
- Mode Manager: Gerenciamento de modos (WORK, IDLE, LEARN, etc.)
- Priorities: Sistema de priorização de tarefas
- Triggers: Sistema de gatilhos para ações autônomas
- Resilience: Sistema de resiliência e tratamento de erros
"""

from .mode_manager import ModeManager, Mode
from .priorities import PriorityManager, PriorityLevel
from .triggers import TriggerManager, Trigger
from .resilience import ResilienceManager, ErrorContext, ErrorSeverity, RecoveryStrategy, safe_execute

__all__ = [
    'ModeManager',
    'Mode',
    'PriorityManager',
    'PriorityLevel',
    'TriggerManager',
    'Trigger',
    'ResilienceManager',
    'ErrorContext',
    'ErrorSeverity',
    'RecoveryStrategy',
    'safe_execute'
]