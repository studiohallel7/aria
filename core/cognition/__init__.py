"""
Módulo de Cognição do Agente.

Separação fundamental:
- Pensamento (thinking.py): Processo interno NÃO visível
- Comunicação (communication.py): Resposta visível ao usuário
- Intenção (intention.py): Decisão de agir ou não
- Planner (planner.py): Planejamento de ações
- Reflection (reflection.py): Aprendizado pós-ação
"""

from .thinking import ThinkingEngine, ThoughtStep, ThinkingProcess
from .communication import CommunicationEngine, UserResponse, CognitiveLoop
from .intention import IntentionEngine, Intention
from .planner import Planner, Plan, PlanStep
from .reflection import ReflectionEngine, Reflection

__all__ = [
    'ThinkingEngine',
    'ThoughtStep', 
    'ThinkingProcess',
    'CommunicationEngine',
    'UserResponse',
    'CognitiveLoop',
    'IntentionEngine',
    'Intention',
    'Planner',
    'Plan',
    'PlanStep',
    'ReflectionEngine',
    'Reflection'
]