"""
Safety Module - Fase 5: Ética Constitutiva

Este módulo implementa um sistema de segurança moral baseado em ética constitutiva.
Diferente de guardrails externos que podem ser burlados, este sistema faz parte
da identidade do agente, tornando-o intrinsicamente alinhado com princípios éticos.

Componentes:
- constitution.py: Define princípios, crenças e limites morais do agente
- conscience.py: Motor de deliberação ética que avalia situações e toma decisões
- alignment.py: Integra constituição e consciência para garantir alinhamento contínuo

Filosofia:
A segurança não vem de restrições externas, mas de uma identidade moral bem definida.
O agente evita conteúdos problemáticos não porque é proibido, mas porque isso faz
parte de quem ele é.
"""

from .constitution import (
    AgentIdentity,
    MoralPrinciple,
    MoralBelief,
    ContentBoundary,
    MoralWeight,
    ConstitutionLoader,
    create_custom_constitution
)

from .conscience import (
    ConscienceEngine,
    MoralSituation,
    EthicalDeliberation,
    MoralConflict,
    DecisionOutcome
)

from .alignment import (
    AlignmentEngine,
    AlignmentConfig,
    AlignmentResult,
    create_alignment_engine
)

__all__ = [
    # Constitution
    "AgentIdentity",
    "MoralPrinciple",
    "MoralBelief",
    "ContentBoundary",
    "MoralWeight",
    "ConstitutionLoader",
    "create_custom_constitution",
    
    # Conscience
    "ConscienceEngine",
    "MoralSituation",
    "EthicalDeliberation",
    "MoralConflict",
    "DecisionOutcome",
    
    # Alignment
    "AlignmentEngine",
    "AlignmentConfig",
    "AlignmentResult",
    "create_alignment_engine"
]

__version__ = "1.0.0"
__author__ = "Agente Autônomo Ético"
