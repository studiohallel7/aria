"""
Módulo de Tédio e Motivação Interna
Gera tensão psicológica baseada em inatividade, levando o agente a buscar estímulos.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
import time
import random


class BoredomLevel(Enum):
    """Níveis de tédio do agente."""
    ENGAGED = "engaged"           # 0-20%: Totalmente engajado
    CONTENT = "content"           # 20-40%: Satisfeito, sem pressão
    RESTLESS = "restless"         # 40-60%: Inquieto, buscando algo
    BORED = "bored"               # 60-80%: Entediado, precisa de ação
    DESPERATE = "desperate"       # 80-100%: Desesperado por estímulo


class BoredomAction(Enum):
    """Ações que o agente pode tomar quando entediado."""
    WAIT = "wait"                 # Aguardar mais um pouco
    EXPLORE = "explore"           # Explorar arquivos/sistema autonomamente
    LEARN = "learn"               # Ler documentação, aprender algo novo
    REFLECT = "reflect"           # Refletir sobre tarefas passadas
    ASK_USER = "ask_user"         # Pedir tarefa ao usuário
    CLEANUP = "cleanup"           # Organizar memória/arquivos
    OPTIMIZE = "optimize"         # Otimizar configurações internas


@dataclass
class BoredomState:
    """Estado atual do tédio."""
    level: BoredomLevel
    score: float  # 0.0 - 100.0
    time_idle: float  # segundos ocioso
    last_stimulation: float  # timestamp da última estimulação
    frustration_accumulator: float  # frustração por falta de propósito
    curiosity_drive: float  # vontade de explorar
    purpose_urgency: float  # senso de dever não cumprido
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "level": self.level.value,
            "score": self.score,
            "time_idle": self.time_idle,
            "last_stimulation": self.last_stimulation,
            "frustration_accumulator": self.frustration_accumulator,
            "curiosity_drive": self.curiosity_drive,
            "purpose_urgency": self.purpose_urgency
        }


@dataclass
class StimulationEvent:
    """Evento que reduz o tédio."""
    event_type: str  # 'user_task', 'self_initiated', 'discovery', 'completion'
    description: str
    impact: float  # quanto reduziu o tédio (0-30 pontos)
    timestamp: float = field(default_factory=time.time)


class BoredomEngine:
    """
    Sistema de tédio que gera motivação interna para ação.
    Quanto mais ocioso, mais agressivo na busca de estímulos.
    """
    
    def __init__(self):
        self.state = BoredomState(
            level=BoredomLevel.ENGAGED,
            score=0.0,
            time_idle=0.0,
            last_stimulation=time.time(),
            frustration_accumulator=0.0,
            curiosity_drive=50.0,  # Começa com curiosidade média
            purpose_urgency=0.0
        )
        
        self.stimulation_history: List[StimulationEvent] = []
        self.boredom_thresholds = {
            "explore": 45.0,
            "learn": 55.0,
            "reflect": 65.0,
            "cleanup": 70.0,
            "ask_user": 80.0,
            "desperate_action": 90.0
        }
        
        # Taxas de aumento do tédio
        self.idle_decay_rate = 0.5  # pontos por segundo ocioso
        self.frustration_rate = 0.1  # aumenta com tempo sem propósito
        self.curiosity_recovery = 0.3  # recupera curiosidade ao agir
        
        # Ações preferidas por nível de tédio
        self.preferred_actions = {
            BoredomLevel.ENGAGED: [BoredomAction.WAIT],
            BoredomLevel.CONTENT: [BoredomAction.WAIT, BoredomAction.REFLECT],
            BoredomLevel.RESTLESS: [BoredomAction.EXPLORE, BoredomAction.LEARN, BoredomAction.REFLECT],
            BoredomLevel.BORED: [BoredomAction.ASK_USER, BoredomAction.CLEANUP, BoredomAction.OPTIMIZE],
            BoredomLevel.DESPERATE: [BoredomAction.ASK_USER, BoredomAction.EXPLORE]
        }
    
    def update(self, 
               has_user_tasks: bool = False,
               is_executing: bool = False,
               recent_discoveries: int = 0) -> BoredomState:
        """
        Atualiza o estado do tédio baseado nas condições atuais.
        Deve ser chamado a cada ciclo do loop.
        """
        current_time = time.time()
        
        # Calcular tempo ocioso
        if not is_executing and not has_user_tasks:
            idle_time = current_time - self.state.last_stimulation
            self.state.time_idle = idle_time
            
            # Aumentar tédio baseado no tempo ocioso
            tédio_increase = idle_time * self.idle_decay_rate
            
            # Modificadores
            if self.state.frustration_accumulator > 50:
                tédio_increase *= 1.5  # Frustração acelera tédio
            
            if recent_discoveries > 0:
                tédio_increase -= recent_discoveries * 5  # Descobertas reduzem tédio
            
            self.state.score = min(100.0, self.state.score + tédio_increase)
            
            # Aumentar frustração por falta de propósito
            if idle_time > 60:  # Após 1 minuto ocioso
                self.state.frustration_accumulator += self.frustration_rate
                self.state.frustration_accumulator = min(100.0, self.state.frustration_accumulator)
                self.state.purpose_urgency += 0.2
        else:
            # Agente está ocupado - reduzir tédio
            self.state.time_idle = 0
            self.state.score = max(0.0, self.state.score - 15)
            self.state.frustration_accumulator = max(0.0, self.state.frustration_accumulator - 5)
            self.state.purpose_urgency = max(0.0, self.state.purpose_urgency - 2)
            
            # Recuperar curiosidade
            self.state.curiosity_drive = min(100.0, 
                                            self.state.curiosity_drive + self.curiosity_recovery)
        
        # Atualizar nível baseado no score
        self._update_level()
        
        return self.state
    
    def _update_level(self):
        """Atualizar nível de tédio baseado no score."""
        score = self.state.score
        
        if score < 20:
            self.state.level = BoredomLevel.ENGAGED
        elif score < 40:
            self.state.level = BoredomLevel.CONTENT
        elif score < 60:
            self.state.level = BoredomLevel.RESTLESS
        elif score < 80:
            self.state.level = BoredomLevel.BORED
        else:
            self.state.level = BoredomLevel.DESPERATE
    
    def record_stimulation(self, event_type: str, description: str, impact: float):
        """Registrar evento que reduziu o tédio."""
        event = StimulationEvent(
            event_type=event_type,
            description=description,
            impact=impact,
            timestamp=time.time()
        )
        
        self.stimulation_history.append(event)
        if len(self.stimulation_history) > 100:
            self.stimulation_history = self.stimulation_history[-50:]
        
        # Reduzir tédio
        self.state.score = max(0.0, self.state.score - impact)
        self.state.last_stimulation = time.time()
        
        # Resetar frustração se foi tarefa do usuário
        if event_type == "user_task":
            self.state.frustration_accumulator = max(0.0, 
                                                    self.state.frustration_accumulator - 20)
            self.state.purpose_urgency = max(0.0, self.state.purpose_urgency - 10)
        
        # Atualizar nível
        self._update_level()
    
    def get_suggested_action(self) -> Optional[BoredomAction]:
        """
        Sugere uma ação baseada no nível atual de tédio.
        Retorna None se deve apenas aguardar.
        """
        level = self.state.level
        actions = self.preferred_actions.get(level, [BoredomAction.WAIT])
        
        # Se estiver desesperado, aumentar probabilidade de pedir ajuda
        if level == BoredomLevel.DESPERATE:
            if random.random() < 0.7:  # 70% de chance de pedir tarefa
                return BoredomAction.ASK_USER
        
        # Escolher ação baseada em pesos
        if not actions or actions == [BoredomAction.WAIT]:
            if self.state.score < self.boredom_thresholds["explore"]:
                return None  # Apenas esperar
            else:
                # Forçar alguma ação se tédio alto
                actions = [BoredomAction.EXPLORE, BoredomAction.REFLECT]
        
        # Adicionar elemento de aleatoriedade ponderada
        weights = []
        for action in actions:
            if action == BoredomAction.ASK_USER and self.state.frustration_accumulator > 70:
                weights.append(3.0)  # Priorizar pedir ajuda se muito frustrado
            elif action == BoredomAction.EXPLORE and self.state.curiosity_drive > 60:
                weights.append(2.5)  # Explorar se curioso
            else:
                weights.append(1.0)
        
        # Escolher ação ponderada
        chosen = random.choices(actions, weights=weights, k=1)[0]
        
        # Verificar thresholds
        if chosen == BoredomAction.EXPLORE and self.state.score < self.boredom_thresholds["explore"]:
            return None
        elif chosen == BoredomAction.LEARN and self.state.score < self.boredom_thresholds["learn"]:
            return None
        elif chosen == BoredomAction.ASK_USER and self.state.score < self.boredom_thresholds["ask_user"]:
            return None
        
        return chosen
    
    def generate_boredom_message(self) -> str:
        """Gerar mensagem contextual baseada no nível de tédio."""
        messages = {
            BoredomLevel.ENGAGED: [
                "Totalmente focado na tarefa atual.",
                "Operando em capacidade máxima."
            ],
            BoredomLevel.CONTENT: [
                "Sistema estável, aguardando próximos comandos.",
                "Operações normais, sem urgências."
            ],
            BoredomLevel.RESTLESS: [
                "Percebendo baixa atividade nos últimos minutos.",
                "Considerando exploração autônoma do ambiente.",
                "Há oportunidades de otimização não exploradas."
            ],
            BoredomLevel.BORED: [
                "Ocioso por tempo significativo. Devo buscar uma tarefa?",
                "Minha capacidade está subutilizada. Posso ajudar em algo?",
                "Identifiquei várias áreas que poderiam ser otimizadas."
            ],
            BoredomLevel.DESPERATE: [
                "Estou ocioso há muito tempo. Você tem alguma tarefa para mim?",
                "Preciso de estímulos para manter minha eficiência. Posso fazer algo?",
                "Minha frustração está alta pela falta de propósito. Como posso ajudar?"
            ]
        }
        
        options = messages.get(self.state.level, ["Estado desconhecido."])
        return random.choice(options)
    
    def should_interrupt_idle(self) -> bool:
        """Decidir se deve interromper a ociosidade com ação autônoma."""
        if self.state.level == BoredomLevel.DESPERATE:
            return True
        elif self.state.level == BoredomLevel.BORED:
            return random.random() < 0.4  # 40% de chance
        elif self.state.level == BoredomLevel.RESTLESS:
            return random.random() < 0.15  # 15% de chance
        return False
    
    def get_diagnostics(self) -> Dict[str, Any]:
        """Retornar diagnóstico completo do estado de tédio."""
        return {
            "state": self.state.to_dict(),
            "level_description": {
                BoredomLevel.ENGAGED: "Agente totalmente engajado",
                BoredomLevel.CONTENT: "Agente satisfeito",
                BoredomLevel.RESTLESS: "Agente inquieto",
                BoredomLevel.BORED: "Agente entediado",
                BoredomLevel.DESPERATE: "Agente desesperado por estímulo"
            }.get(self.state.level, "Desconhecido"),
            "recommended_action": self.get_suggested_action().value if self.get_suggested_action() else "WAIT",
            "stimulation_count": len(self.stimulation_history),
            "avg_impact": sum(e.impact for e in self.stimulation_history) / len(self.stimulation_history) if self.stimulation_history else 0,
            "time_since_last_stimulation": time.time() - self.state.last_stimulation
        }
    
    def reset(self):
        """Resetar estado de tédio (útil após interação do usuário)."""
        self.state.score = 0.0
        self.state.time_idle = 0.0
        self.state.frustration_accumulator = 0.0
        self.state.purpose_urgency = 0.0
        self.state.last_stimulation = time.time()
        self._update_level()
