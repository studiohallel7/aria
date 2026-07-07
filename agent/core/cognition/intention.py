"""
Intention System - Sistema de intenção do agente

Tipos de intenção:
- ACT: Agir/executar ação
- NO_ACT: Não agir, apenas observar
- EXPLORE: Explorar ativamente
- LEARN: Aprender/criar memória
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional, List, Dict
import random


class IntentionType(Enum):
    ACT = "act"           # Executar ação específica
    NO_ACT = "no_act"     # Não agir
    EXPLORE = "explore"   # Explorar contexto
    LEARN = "learn"       # Aprender/organizar memória
    REFLECT = "reflect"   # Refletir sobre ações passadas
    WAIT = "wait"         # Aguardar condições


@dataclass
class Intention:
    """Representa uma intenção do agente"""
    intention_type: IntentionType
    reason: str
    priority: int = 5  # 1-10
    metadata: Dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class IntentionEngine:
    """
    Motor de decisão de intenções
    
    Avalia contexto interno e externo para determinar
    a próxima intenção do agente
    """
    
    def __init__(self):
        self.current_intention: Optional[Intention] = None
        self.intention_history: List[Intention] = []
    
    def evaluate(
        self,
        has_user_tasks: bool,
        idle_time: float,
        mode: str,
        context_summary: Dict = None,
        errors_recent: int = 0,
        llm_calls_recent: int = 0,
        max_llm_calls: int = 3
    ) -> Intention:
        """
        Avalia condições e determina intenção
        
        Args:
            has_user_tasks: Se existem tarefas do usuário
            idle_time: Tempo ocioso em segundos
            mode: 'work' ou 'free'
            context_summary: Resumo do contexto atual
            errors_recent: Número de erros recentes
            llm_calls_recent: Chamadas LLM no ciclo atual
            max_llm_calls: Máximo de chamadas por ciclo
        
        Returns:
            Intention determinada
        """
        
        # Regra 1: Tarefas do usuário têm prioridade máxima
        if has_user_tasks:
            intention = Intention(
                intention_type=IntentionType.ACT,
                reason="Tarefa do usuário pendente",
                priority=10,
                metadata={"source": "user"}
            )
            self.current_intention = intention
            self.intention_history.append(intention)
            return intention
        
        # Regra 2: Erros recentes limitam ação
        if errors_recent >= 3:
            intention = Intention(
                intention_type=IntentionType.WAIT,
                reason="Muitos erros recentes, aguardando recuperação",
                priority=8,
                metadata={"errors": errors_recent}
            )
            self.current_intention = intention
            self.intention_history.append(intention)
            return intention
        
        # Regra 3: Limite de chamadas LLM atingido
        if llm_calls_recent >= max_llm_calls:
            intention = Intention(
                intention_type=IntentionType.NO_ACT,
                reason="Limite de chamadas LLM no ciclo atingido",
                priority=7,
                metadata={"llm_calls": llm_calls_recent}
            )
            self.current_intention = intention
            self.intention_history.append(intention)
            return intention
        
        # Regra 4: Modo trabalho sem tarefas = não age
        if mode == "work":
            intention = Intention(
                intention_type=IntentionType.NO_ACT,
                reason="Modo trabalho sem tarefas pendentes",
                priority=5
            )
            self.current_intention = intention
            self.intention_history.append(intention)
            return intention
        
        # Regra 5: Modo livre - pode explorar se ocioso há tempo suficiente
        if mode == "free":
            if idle_time > 60:  # 60 segundos ocioso
                # Curiosidade baseada em aleatoriedade controlada
                if random.random() < 0.3:  # 30% de chance
                    intention = Intention(
                        intention_type=IntentionType.EXPLORE,
                        reason="Modo livre, ocioso há {}s, curiosidade ativada".format(int(idle_time)),
                        priority=4,
                        metadata={"idle_time": idle_time, "curiosity": True}
                    )
                    self.current_intention = intention
                    self.intention_history.append(intention)
                    return intention
            
            # Pode usar tempo para aprender/organizar memória
            intention = Intention(
                intention_type=IntentionType.LEARN,
                reason="Modo livre, organizando memória",
                priority=3,
                metadata={"idle_time": idle_time}
            )
            self.current_intention = intention
            self.intention_history.append(intention)
            return intention
        
        # Default: não age
        intention = Intention(
            intention_type=IntentionType.NO_ACT,
            reason="Nenhuma condição de ação atendida",
            priority=1
        )
        self.current_intention = intention
        self.intention_history.append(intention)
        return intention
    
    def get_current_intention(self) -> Optional[Intention]:
        """Retorna intenção atual"""
        return self.current_intention
    
    def get_last_n_intentions(self, n: int = 10) -> List[Intention]:
        """Retorna últimas n intenções"""
        return self.intention_history[-n:]
    
    def clear_history(self):
        """Limpa histórico de intenções"""
        self.intention_history = []
