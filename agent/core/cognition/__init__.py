"""
Módulo de Cognição do Agente.

Separação fundamental:
- Pensamento (thinking.py): Processo interno NÃO visível
- Comunicação (communication.py): Resposta visível ao usuário
- Intenção (intention.py): Decisão de agir ou não
- Planner (planner.py): Planejamento de ações
- Reflection (reflection.py): Aprendizado pós-ação
- Boredom (boredom.py): Sistema de tédio e motivação intrínseca
- Drive (drive.py): Sistema de drives motivacionais
- Critic (critic.py): Crítico interno para validação de planos
- Interpretation (interpretation.py): Interpretação contínua de dados
- Working Set (working_set.py): Memória de trabalho ativa
"""

from .thinking import ThinkingEngine, ThoughtStep, ThinkingProcess
from .communication import CommunicationEngine, UserResponse, CognitiveLoop
from .intention import IntentionEngine, Intention
from .planner import Planner, Plan, PlanStep
from .reflection import ReflectionEngine, Reflection
from .boredom import BoredomEngine, BoredomLevel, BoredomAction
from .drive import DriveSystem, DriveType, MotivationalState
from .critic import InternalCritic, CritiqueReport, CriticSeverity
from .interpretation import ContinuousInterpreter, RawInput, InterpretationLayer, InterpretationResult
from .working_set import WorkingMemorySet, WorkingItem

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
    'Reflection',
    'BoredomEngine',
    'BoredomLevel',
    'BoredomAction',
    'DriveSystem',
    'DriveType',
    'MotivationalState',
    'InternalCritic',
    'CritiqueReport',
    'CriticSeverity',
    'ContinuousInterpreter',
    'RawInput',
    'InterpretationLayer',
    'InterpretationResult',
    'WorkingMemorySet',
    'WorkingItem'
]