"""
🤖 Agente Autônomo - Sistema Cognitivo Completo

Um framework para agentes autônomos com:
- Pensamento autônomo e contínuo
- Memória holográfica e associativa  
- Ética constitutiva intrínseca
- Ferramentas integradas (web, filesystem, shell)
- Multi-provider LLM com failover automático

Arquitetura em 5 Fases:
├── Fase 1: Fundação (config, CLI)
├── Fase 2: Núcleo Cognitivo (thinking, planning, reflection)
├── Fase 3: Infraestrutura LLM (providers, tools, monitoring)
├── Fase 4: Memória Avançada (grafo, consolidação, subconsciente)
└── Fase 5: Ética Constitutiva (constituição, consciência, alignment)

Exemplo de uso:
    from agent import AutonomousAgent
    
    agent = AutonomousAgent(name="Aria")
    agent.start_autonomous_mode()
"""

__version__ = "1.0.0"
__author__ = "Autonomous Agent Project"

from agent.core import cognition, state, autonomy, loop
from agent.infra import llm, tools, accounts, monitoring
from agent.memory import manager as memory_manager
from agent.safety import constitution, conscience, alignment

__all__ = [
    # Versionamento
    "__version__",
    
    # Core modules
    "cognition",
    "state", 
    "autonomy",
    "loop",
    
    # Infrastructure
    "llm",
    "tools",
    "accounts",
    "monitoring",
    
    # Memory
    "memory_manager",
    
    # Safety/Ethics
    "constitution",
    "conscience",
    "alignment",
]

# Convenience imports
def create_agent(name: str = "Agent", config_path: str = None):
    """Factory function para criar um agente configurado."""
    from agent.core.loop.main_loop import AgentLoop
    return AgentLoop(agent_name=name, config_path=config_path)

__all__.append("create_agent")
