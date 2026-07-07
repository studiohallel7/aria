"""
Módulo de Cognição do Agente.

Separação fundamental:
- Pensamento (thinking.py): Processo interno NÃO visível
- Comunicação (communication.py): Resposta visível ao usuário
- Intenção (intention.py): Decisão de agir ou não
- Planner (planner.py): Planejamento de ações
- Reflection (reflection.py): Aprendizado pós-ação
- Boredom (boredom.py): Sistema de tédio e ações autônomas
- Drive (drive.py): Sistema de drives motivacionais
- Critic (critic.py): Crítico interno para validação
- Interpretation (interpretation.py): Interpretação contínua de contexto
- Working Set (working_set.py): Memória de trabalho ativa
- Body Anchor (body_anchor.py): Âncora corporal do agente
"""

from .thinking import ThinkingEngine, ThoughtStep, ThinkingProcess
from .communication import CommunicationEngine, UserResponse, CognitiveLoop
from .intention import IntentionEngine, Intention
from .planner import Planner, Plan, PlanStep
from .reflection import ReflectionEngine, Reflection
from .boredom import BoredomEngine, BoredomAction, BoredomState
from .drive import DriveSystem, DriveType, MotivationalState
from .critic import InternalCritic, Critique, CritiqueReport, CriticSeverity
from .interpretation import ContinuousInterpreter, RawInput, Interpretation
from .working_set import WorkingMemorySet, WorkingItem
from .body_anchor import BodyAnchor, BodyPart, BodyState as BodyAnchorState, SensoryChannel, MotorActuator, BodyComponent, SensoryModality, MotorCapability

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
    'BoredomAction',
    'BoredomState',
    'DriveSystem',
    'DriveType',
    'MotivationalState',
    'InternalCritic',
    'Critique',
    'CritiqueReport',
    'CriticSeverity',
    'ContinuousInterpreter',
    'RawInput',
    'Interpretation',
    'WorkingMemorySet',
    'WorkingItem',
    'BodyAnchor',
    'BodyPart',
    'BodyAnchorState',
    'SensoryChannel',
    'MotorActuator',
    'BodyComponent',
    'SensoryModality',
    'MotorCapability'
]