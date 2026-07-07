"""
Agente Autônomo - Sistema Cognitivo Completo

Arquitetura unificada com 5 fases:
- Fase 1: Fundação (configuração, CLI)
- Fase 2: Núcleo Cognitivo (pensamento, planejamento, reflexão)
- Fase 3: Infraestrutura LLM (providers, tools, monitoring)
- Fase 4: Memória Avançada (holográfica, consolidação, subconsciente)
- Fase 5: Ética Constitutiva (constituição, consciência, alignment)
"""

from agent.core import cognition, state, autonomy, loop
from agent.infra import llm, tools, accounts, monitoring
from agent.memory import manager
from agent.safety import constitution, conscience, alignment

__version__ = "1.0.0"
__all__ = [
    # Core
    "cognition",
    "state", 
    "autonomy",
    "loop",
    
    # Infraestrutura
    "llm",
    "tools",
    "accounts",
    "monitoring",
    
    # Memória
    "manager",
    
    # Segurança/Ética
    "constitution",
    "conscience",
    "alignment",
]