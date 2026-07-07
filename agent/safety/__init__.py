"""
Safety Module - Módulo de Segurança e Alinhamento Ético do Agente

Este módulo fornece:
- Constitution: Definição de princípios morais e crenças
- Conscience: Motor de deliberação ética
- Alignment: Engine de alinhamento moral
- IdentityCore: Núcleo de identidade e verificação de vínculos
"""

from .constitution import (
    AgentIdentity,
    ConstitutionLoader,
    MoralPrinciple,
    MoralBelief,
    ContentBoundary,
    MoralWeight,
    create_custom_constitution
)

from .conscience import (
    ConscienceEngine,
    MoralSituation,
    EthicalDeliberation,
    DecisionOutcome
)

from .alignment import (
    AlignmentEngine,
    AlignmentConfig,
    AlignmentResult,
    create_alignment_engine
)

from .identity_core import (
    IdentityCore,
    TrustLevel,
    VerificationMethod,
    IdentityClaim,
    RelationshipBond,
    VerificationResult,
    get_identity_core,
    reset_identity_core
)

__all__ = [
    # Constituição
    "AgentIdentity",
    "ConstitutionLoader",
    "MoralPrinciple",
    "MoralBelief",
    "ContentBoundary",
    "MoralWeight",
    "create_custom_constitution",
    
    # Consciência
    "ConscienceEngine",
    "MoralSituation",
    "EthicalDeliberation",
    "DecisionOutcome",
    
    # Alignment
    "AlignmentEngine",
    "AlignmentConfig",
    "AlignmentResult",
    "create_alignment_engine",
    
    # Identidade
    "IdentityCore",
    "TrustLevel",
    "VerificationMethod",
    "IdentityClaim",
    "RelationshipBond",
    "VerificationResult",
    "get_identity_core",
    "reset_identity_core"
]
