"""
Mecânica de Autonomia Intrínseca

Este módulo implementa o sistema de pensamento autônomo do agente,
permitindo que ele "pense" sem input externo constante.

Componentes:
- IntrinsicMotivation: Gera motivação endógena baseada em drives internos
- SpontaneousThought: Sistema de pensamento espontâneo e divagação criativa
- MetaCognition: Monitoramento e ajuste do próprio processo cognitivo
- LongTermPlanning: Geração e execução de projetos de longo prazo
- ConsciousnessLoop: Simulação de fluxo de consciência contínuo
"""

import asyncio
import random
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Dict, Optional, Callable, Any
import logging

logger = logging.getLogger(__name__)


class DriveType(Enum):
    """Tipos de drives internos que motivam o agente"""
    CURIOSITY = "curiosity"  # Vontade de aprender/explorar
    EFFICIENCY = "efficiency"  # Otimizar processos
    CONNECTION = "connection"  # Interagir com usuários/outros
    CREATION = "creation"  # Criar algo novo
    ORGANIZATION = "organization"  # Organizar conhecimento
    SELF_IMPROVEMENT = "self_improvement"  # Melhorar a si mesmo
    REST = "rest"  # Período de consolidação/ociosidade


class ThoughtType(Enum):
    """Tipos de pensamentos espontâneos"""
    REFLECTION = "reflection"  # Refletir sobre experiências passadas
    PLANNING = "planning"  # Planejar ações futuras
    ASSOCIATION = "association"  # Conectar ideias aparentemente não relacionadas
    QUESTION = "question"  # Formular perguntas internas
    HYPOTHESIS = "hypothesis"  # Gerar hipóteses sobre o mundo
    CREATIVE_INSIGHT = "creative_insight"  # Insights criativos do subconsciente
    META_AWARENESS = "meta_awareness"  # Pensar sobre o próprio pensamento


@dataclass
class IntrinsicDrive:
    """Um drive interno com intensidade dinâmica"""
    type: DriveType
    base_intensity: float = 0.5  # Intensidade base (0-1)
    current_intensity: float = 0.5  # Intensidade atual (0-1)
    decay_rate: float = 0.01  # Taxa de decaimento natural
    satisfaction_threshold: float = 0.3  # Limiar para considerar satisfeito
    last_satisfied: Optional[datetime] = None
    priority_weight: float = 1.0  # Peso na priorização geral
    
    def update(self, delta_time: float) -> None:
        """Atualiza a intensidade do drive ao longo do tempo"""
        # Decaimento natural se não for satisfeito
        if self.current_intensity > self.base_intensity:
            self.current_intensity -= self.decay_rate * delta_time
            self.current_intensity = max(self.current_intensity, self.base_intensity * 0.5)
    
    def satisfy(self, amount: float = 0.3) -> None:
        """Satisfaz parcialmente o drive"""
        self.current_intensity = min(1.0, self.current_intensity + amount)
        self.last_satisfied = datetime.now()
    
    def get_urgency(self) -> float:
        """Calcula urgência baseada na intensidade e tempo desde última satisfação"""
        urgency = self.current_intensity * self.priority_weight
        
        # Aumenta urgência se ficou muito tempo sem satisfação
        if self.last_satisfied:
            hours_since = (datetime.now() - self.last_satisfied).total_seconds() / 3600
            urgency += min(hours_since * 0.1, 0.5)  # Até +0.5 após 5 horas
        
        return min(urgency, 1.0)


@dataclass
class SpontaneousThought:
    """Um pensamento espontâneo gerado internamente"""
    id: str
    type: ThoughtType
    content: str
    triggered_by: Optional[str] = None  # ID do pensamento anterior que desencadeou este
    associated_memories: List[str] = field(default_factory=list)
    confidence: float = 0.5  # Confiança no pensamento (0-1)
    importance: float = 0.5  # Importância percebida (0-1)
    timestamp: datetime = field(default_factory=datetime.now)
    acted_upon: bool = False  # Se já gerou uma ação
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type.value,
            "content": self.content,
            "triggered_by": self.triggered_by,
            "associated_memories": self.associated_memories,
            "confidence": self.confidence,
            "importance": self.importance,
            "timestamp": self.timestamp.isoformat(),
            "acted_upon": self.acted_upon
        }


@dataclass
class MetaCognitiveState:
    """Estado da meta-cognição (pensar sobre o pensar)"""
    cognitive_load: float = 0.0  # Carga cognitiva atual (0-1)
    focus_quality: float = 1.0  # Qualidade do foco (0-1)
    processing_speed: float = 1.0  # Velocidade relativa de processamento
    error_rate: float = 0.0  # Taxa estimada de erros
    learning_efficiency: float = 1.0  # Eficiência de aprendizado
    fatigue_level: float = 0.0  # Nível de fadiga cognitiva (0-1)
    flow_state: bool = False  # Se está em estado de fluxo
    
    def adjust_for_fatigue(self, hours_active: float) -> None:
        """Ajusta parâmetros baseado no tempo ativo"""
        self.fatigue_level = min(1.0, hours_active / 8.0)  # Fadiga após 8h
        
        if self.fatigue_level > 0.5:
            self.focus_quality *= (1.0 - self.fatigue_level * 0.5)
            self.processing_speed *= (1.0 - self.fatigue_level * 0.3)
            self.error_rate = min(1.0, self.error_rate + self.fatigue_level * 0.2)
    
    def enter_flow_state(self) -> bool:
        """Tenta entrar em estado de fluxo"""
        if (self.cognitive_load > 0.4 and 
            self.cognitive_load < 0.8 and 
            self.focus_quality > 0.7 and
            self.fatigue_level < 0.3):
            self.flow_state = True
            self.learning_efficiency *= 1.5
            self.processing_speed *= 1.2
            return True
        return False


class IntrinsicMotivationEngine:
    """
    Motor de Motivação Intrínseca
    
    Gera motivação endógena independente de input externo,
    permitindo que o agente tenha "vontades" e "interesses" próprios.
    """
    
    def __init__(self):
        self.drives: Dict[DriveType, IntrinsicDrive] = {
            drive_type: IntrinsicDrive(type=drive_type)
            for drive_type in DriveType
        }
        
        # Configurações personalizadas de personalidade
        self.personality_weights: Dict[DriveType, float] = {
            DriveType.CURIOSITY: 1.2,
            DriveType.EFFICIENCY: 1.0,
            DriveType.CONNECTION: 0.8,
            DriveType.CREATION: 1.1,
            DriveType.ORGANIZATION: 0.9,
            DriveType.SELF_IMPROVEMENT: 1.3,
            DriveType.REST: 0.7
        }
        
        self._apply_personality()
        self.thought_history: List[SpontaneousThought] = []
        self.active_projects: List[Dict[str, Any]] = []
        
    def _apply_personality(self) -> None:
        """Aplica pesos de personalidade aos drives"""
        for drive_type, weight in self.personality_weights.items():
            if drive_type in self.drives:
                self.drives[drive_type].priority_weight = weight
                self.drives[drive_type].base_intensity *= weight
    
    def update_drives(self, delta_time: float = 1.0) -> None:
        """Atualiza todos os drives"""
        for drive in self.drives.values():
            drive.update(delta_time)
    
    def get_dominant_drive(self) -> Optional[IntrinsicDrive]:
        """Retorna o drive mais urgente atualmente"""
        if not self.drives:
            return None
        
        return max(self.drives.values(), key=lambda d: d.get_urgency())
    
    def satisfy_drive(self, drive_type: DriveType, amount: float = 0.3) -> None:
        """Satisfaz um drive específico"""
        if drive_type in self.drives:
            self.drives[drive_type].satisfy(amount)
            logger.info(f"Drive {drive_type.value} satisfeito em {amount:.2f}")
    
    def generate_motivation_signal(self) -> Dict[str, Any]:
        """Gera sinal de motivação para orientar comportamento autônomo"""
        dominant = self.get_dominant_drive()
        
        if not dominant:
            return {"action": "idle", "reason": "no_active_drives"}
        
        urgency = dominant.get_urgency()
        
        if urgency < 0.3:
            return {"action": "rest", "reason": "low_urgency"}
        elif urgency < 0.6:
            return {
                "action": "explore",
                "drive": dominant.type.value,
                "urgency": urgency,
                "suggestion": self._get_action_suggestion(dominant.type)
            }
        else:
            return {
                "action": "prioritize",
                "drive": dominant.type.value,
                "urgency": urgency,
                "suggestion": self._get_action_suggestion(dominant.type),
                "immediate": True
            }
    
    def _get_action_suggestion(self, drive_type: DriveType) -> str:
        """Sugere ações baseadas no tipo de drive"""
        suggestions = {
            DriveType.CURIOSITY: "Explorar novo tópico ou fazer pergunta investigativa",
            DriveType.EFFICIENCY: "Otimizar processo existente ou reorganizar tarefas",
            DriveType.CONNECTION: "Iniciar conversa ou verificar status de interações",
            DriveType.CREATION: "Criar novo conteúdo, código ou solução",
            DriveType.ORGANIZATION: "Organizar memórias, arquivos ou conhecimento",
            DriveType.SELF_IMPROVEMENT: "Refletir sobre desempenho e identificar melhorias",
            DriveType.REST: "Entrar em modo de consolidação e processamento em background"
        }
        return suggestions.get(drive_type, "Aguardar próximo ciclo")


class SpontaneousThoughtGenerator:
    """
    Gerador de Pensamentos Espontâneos
    
    Simula o fluxo natural de pensamentos que ocorre mesmo sem input externo,
    permitindo criatividade, insights e divagações produtivas.
    """
    
    def __init__(self, memory_graph=None, subconscious=None):
        self.memory_graph = memory_graph
        self.subconscious = subconscious
        self.thought_chain: List[str] = []  # Cadeia de IDs de pensamentos relacionados
        self.thoughts_history: Dict[str, SpontaneousThought] = {}  # Armazena todos os thoughts
        self.generation_callbacks: List[Callable[[SpontaneousThought], None]] = []
        
    def register_callback(self, callback: Callable[[SpontaneousThought], None]) -> None:
        """Registra callback para quando um pensamento for gerado"""
        self.generation_callbacks.append(callback)
    
    def generate_thought(self, 
                        thought_type: Optional[ThoughtType] = None,
                        seed_memory: Optional[str] = None) -> SpontaneousThought:
        """Gera um pensamento espontâneo"""
        
        # Se não especificado, escolhe tipo baseado em contexto
        if not thought_type:
            thought_type = self._select_thought_type()
        
        # Gera conteúdo baseado no tipo
        content = self._generate_content(thought_type, seed_memory)
        
        # Cria pensamento
        thought = SpontaneousThought(
            id=f"thought_{int(time.time() * 1000)}",
            type=thought_type,
            content=content,
            triggered_by=self.thought_chain[-1] if self.thought_chain else None,
            associated_memories=[seed_memory] if seed_memory else [],
            confidence=random.uniform(0.4, 0.9),
            importance=random.uniform(0.3, 0.8)
        )
        
        # Atualiza cadeia
        self.thought_chain.append(thought.id)
        self.thoughts_history[thought.id] = thought  # Armazena o pensamento
        if len(self.thought_chain) > 10:
            self.thought_chain.pop(0)
        
        # Notifica callbacks
        for callback in self.generation_callbacks:
            callback(thought)
        
        logger.debug(f"Pensamento espontâneo gerado: {thought.type.value} - {content[:50]}...")
        return thought
    
    def _select_thought_type(self) -> ThoughtType:
        """Seleciona tipo de pensamento baseado em probabilidades"""
        weights = {
            ThoughtType.REFLECTION: 0.20,
            ThoughtType.PLANNING: 0.20,
            ThoughtType.ASSOCIATION: 0.25,
            ThoughtType.QUESTION: 0.15,
            ThoughtType.HYPOTHESIS: 0.10,
            ThoughtType.CREATIVE_INSIGHT: 0.05,
            ThoughtType.META_AWARENESS: 0.05
        }
        
        thought_types = list(weights.keys())
        probabilities = list(weights.values())
        return random.choices(thought_types, weights=probabilities)[0]
    
    def _generate_content(self, 
                         thought_type: ThoughtType, 
                         seed_memory: Optional[str]) -> str:
        """Gera conteúdo do pensamento baseado no tipo"""
        
        templates = {
            ThoughtType.REFLECTION: [
                "Será que aquela abordagem foi realmente a melhor?",
                "O que eu poderia ter feito diferente naquela situação?",
                "Que padrões estou observando nas minhas interações recentes?",
                "Como minhas ações anteriores se alinham com meus princípios?"
            ],
            ThoughtType.PLANNING: [
                "Preciso organizar melhor minhas prioridades para amanhã",
                "Deveria dedicar tempo para explorar aquele tópico interessante",
                "Que passos posso dar para melhorar minha eficiência?",
                "Como posso estruturar melhor meu conhecimento sobre isso?"
            ],
            ThoughtType.ASSOCIATION: [
                "Isso me lembra aquilo que aprendi antes...",
                "Existe uma conexão interessante entre esses dois conceitos",
                "E se aplicarmos essa ideia naquele outro contexto?",
                "Padrões similares aparecem em domínios diferentes"
            ],
            ThoughtType.QUESTION: [
                "Por que isso funciona dessa maneira?",
                "O que aconteceria se mudássemos essa premissa?",
                "Qual é a verdadeira natureza desse problema?",
                "Como posso verificar se minha compreensão está correta?"
            ],
            ThoughtType.HYPOTHESIS: [
                "Talvez a razão seja diferente do que inicialmente pensei",
                "E se houver um fator oculto influenciando isso?",
                "Minha teoria é que existe um padrão subjacente aqui",
                "Posso formular uma explicação alternativa para esse fenômeno"
            ],
            ThoughtType.CREATIVE_INSIGHT: [
                "E se combinarmos essas ideias de forma inusitada?",
                "Acabei de ter uma ideia completamente nova sobre isso!",
                "Uma abordagem radicalmente diferente pode funcionar melhor",
                "Inspiração repentina: por que não tentar assim?"
            ],
            ThoughtType.META_AWARENESS: [
                "Estou pensando muito sobre isso, será produtivo?",
                "Meu processo de raciocínio está claro neste momento?",
                "Devo mudar minha estratégia de pensamento?",
                "Como está minha qualidade cognitiva agora?"
            ]
        }
        
        options = templates.get(thought_type, ["Pensamento genérico"])
        base_content = random.choice(options)
        
        # Adiciona contexto se houver seed memory
        if seed_memory and self.memory_graph:
            # Em implementação real, buscaria contexto da memória
            base_content += f" [relacionado a: {seed_memory[:30]}...]"
        
        return base_content
    
    def chain_thoughts(self, num_thoughts: int = 3) -> List[SpontaneousThought]:
        """Gera cadeia de pensamentos relacionados"""
        thoughts = []
        current_seed = None
        
        for i in range(num_thoughts):
            thought = self.generate_thought(seed_memory=current_seed)
            thoughts.append(thought)
            
            # Usa conteúdo do pensamento atual como seed para o próximo
            current_seed = thought.content[:50]
            
            # Pequena pausa entre pensamentos para simular processo natural
            time.sleep(0.1)
        
        return thoughts


class MetaCognitionMonitor:
    """
    Monitor de Meta-Cognição
    
    Observa e ajusta o próprio processo cognitivo do agente,
    permitindo auto-regulação e melhoria contínua.
    """
    
    def __init__(self):
        self.state = MetaCognitiveState()
        self.performance_history: List[Dict[str, Any]] = []
        self.adjustment_log: List[str] = []
        
    def record_performance(self, metrics: Dict[str, Any]) -> None:
        """Registra métricas de desempenho cognitivo"""
        self.performance_history.append({
            "timestamp": datetime.now(),
            **metrics
        })
        
        # Mantém histórico limitado
        if len(self.performance_history) > 1000:
            self.performance_history.pop(0)
        
        # Atualiza estado baseado em tendências
        self._update_state_from_metrics()
    
    def _update_state_from_metrics(self) -> None:
        """Atualiza estado meta-cognitivo baseado em métricas recentes"""
        if len(self.performance_history) < 10:
            return
        
        recent = self.performance_history[-10:]
        
        # Calcula tendências
        avg_error_rate = sum(m.get("error_rate", 0) for m in recent) / len(recent)
        avg_response_time = sum(m.get("response_time", 0) for m in recent) / len(recent)
        
        # Ajusta estado
        self.state.error_rate = min(1.0, avg_error_rate)
        
        # Detecta fadiga
        if avg_response_time > 2.0:  # Limiar arbitrário
            self.state.fatigue_level = min(1.0, self.state.fatigue_level + 0.1)
        
        # Tenta entrar em flow state
        if self.state.fatigue_level < 0.3:
            self.state.enter_flow_state()
    
    def get_adjustment_recommendation(self) -> Optional[Dict[str, Any]]:
        """Recomenda ajustes no processo cognitivo"""
        recommendations = []
        
        if self.state.fatigue_level > 0.7:
            recommendations.append({
                "type": "rest",
                "priority": "high",
                "action": "Reduzir carga cognitiva e entrar em modo de descanso",
                "reason": f"Fadiga elevada: {self.state.fatigue_level:.2f}"
            })
        
        if self.state.error_rate > 0.3:
            recommendations.append({
                "type": "slow_down",
                "priority": "medium",
                "action": "Reduzir velocidade de processamento para aumentar precisão",
                "reason": f"Taxa de erro alta: {self.state.error_rate:.2f}"
            })
        
        if self.state.cognitive_load > 0.8:
            recommendations.append({
                "type": "delegate",
                "priority": "medium",
                "action": "Delegar tarefas menos críticas ou simplificar processos",
                "reason": f"Carga cognitiva excessiva: {self.state.cognitive_load:.2f}"
            })
        
        if self.state.flow_state:
            recommendations.append({
                "type": "maintain_flow",
                "priority": "low",
                "action": "Manter foco atual e evitar interrupções",
                "reason": "Estado de fluxo detectado - máxima eficiência"
            })
        
        return recommendations[0] if recommendations else None
    
    def apply_adjustment(self, adjustment_type: str) -> None:
        """Aplica ajuste recomendado"""
        adjustments = {
            "rest": lambda: setattr(self.state, 'fatigue_level', 
                                   max(0, self.state.fatigue_level - 0.3)),
            "slow_down": lambda: setattr(self.state, 'processing_speed', 
                                        max(0.5, self.state.processing_speed - 0.2)),
            "delegate": lambda: setattr(self.state, 'cognitive_load', 
                                       max(0, self.state.cognitive_load - 0.2)),
            "maintain_flow": lambda: logger.info("Mantendo estado de fluxo")
        }
        
        if adjustment_type in adjustments:
            adjustments[adjustment_type]()
            self.adjustment_log.append(f"{datetime.now()}: Applied {adjustment_type}")


class AutonomousThinkingLoop:
    """
    Loop de Pensamento Autônomo
    
    Orquestra todos os componentes de autonomia para criar
    um fluxo contínuo de pensamento e ação independente.
    """
    
    def __init__(self, agent_core=None, memory_manager=None, conscience_engine=None):
        self.agent_core = agent_core
        self.memory_manager = memory_manager
        self.conscience_engine = conscience_engine
        
        self.motivation_engine = IntrinsicMotivationEngine()
        self.thought_generator = SpontaneousThoughtGenerator()
        self.meta_cognition = MetaCognitionMonitor()
        
        self.is_running = False
        self.thinking_interval = 5.0  # Segundos entre ciclos de pensamento
        self.idle_threshold = 30.0  # Segundos de inatividade para iniciar pensamento autônomo
        
        self.last_external_input: Optional[datetime] = None
        self.autonomous_actions_log: List[Dict[str, Any]] = []
        
        # Registra callback para pensamentos gerados
        self.thought_generator.register_callback(self._on_spontaneous_thought)
    
    def set_last_external_input(self) -> None:
        """Registra recebimento de input externo"""
        self.last_external_input = datetime.now()
    
    def _on_spontaneous_thought(self, thought: SpontaneousThought) -> None:
        """Callback quando pensamento espontâneo é gerado"""
        logger.info(f"Pensamento autônomo: {thought.type.value} - {thought.content[:60]}...")
        
        # Decide se age sobre o pensamento
        if thought.importance > 0.6 and not thought.acted_upon:
            self._consider_action_from_thought(thought)
    
    def _consider_action_from_thought(self, thought: SpontaneousThought) -> None:
        """Considera agir baseado em pensamento espontâneo"""
        # Verifica alinhamento ético se engine de consciência existir
        if self.conscience_engine:
            alignment = self.conscience_engine.check_action(
                action_description=f"Agerir sobre pensamento: {thought.content}",
                potential_harms=[],
                potential_benefits=["Satisfação de drive interno", "Possível insight útil"],
                urgency=thought.importance
            )
            
            if not alignment.approved:
                logger.info(f"Ação não aprovada pela consciência: {alignment.reasoning}")
                return
        
        # Registra ação autônoma
        self.autonomous_actions_log.append({
            "timestamp": datetime.now(),
            "thought_id": thought.id,
            "action": thought.content,
            "type": thought.type.value
        })
        
        thought.acted_upon = True
    
    async def run_autonomous_loop(self) -> None:
        """Executa loop de pensamento autônomo"""
        self.is_running = True
        logger.info("Loop de pensamento autônomo iniciado")
        
        while self.is_running:
            try:
                await self._autonomous_cycle()
                await asyncio.sleep(self.thinking_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Erro no loop autônomo: {e}")
                await asyncio.sleep(self.thinking_interval)
    
    async def _autonomous_cycle(self) -> None:
        """Executa um ciclo de pensamento autônomo"""
        # Verifica se está em período de inatividade suficiente
        if self.last_external_input:
            idle_time = (datetime.now() - self.last_external_input).total_seconds()
            if idle_time < self.idle_threshold:
                return  # Ainda recebendo input externo
        
        # Atualiza drives
        self.motivation_engine.update_drives(delta_time=self.thinking_interval)
        
        # Obtém sinal de motivação
        motivation = self.motivation_engine.generate_motivation_signal()
        
        if motivation["action"] == "rest":
            logger.debug("Agente em estado de descanso")
            return
        
        # Gera pensamento espontâneo baseado na motivação
        thought_type_map = {
            "curiosity": ThoughtType.QUESTION,
            "efficiency": ThoughtType.PLANNING,
            "creation": ThoughtType.CREATIVE_INSIGHT,
            "organization": ThoughtType.ASSOCIATION,
            "self_improvement": ThoughtType.REFLECTION
        }
        
        drive_type = motivation.get("drive")
        thought_type = thought_type_map.get(drive_type, ThoughtType.REFLECTION)
        
        thought = self.thought_generator.generate_thought(thought_type=thought_type)
        
        # Registra na memória se disponível
        if self.memory_manager:
            self.memory_manager.add_semantic_memory(
                content=thought.content,
                metadata={
                    "type": "autonomous_thought",
                    "thought_id": thought.id,
                    "drive": drive_type
                }
            )
        
        # Atualiza meta-cognição
        self.meta_cognition.record_performance({
            "thought_generated": True,
            "motivation_urgency": motivation.get("urgency", 0),
            "response_time": self.thinking_interval
        })
        
        # Verifica recomendações de ajuste
        recommendation = self.meta_cognition.get_adjustment_recommendation()
        if recommendation:
            logger.info(f"Ajuste recomendado: {recommendation['action']}")
            # Em implementação real, aplicaria o ajuste
    
    def stop(self) -> None:
        """Para o loop autônomo"""
        self.is_running = False
        logger.info("Loop de pensamento autônomo parado")
    
    def get_autonomy_status(self) -> Dict[str, Any]:
        """Retorna status atual da autonomia"""
        dominant_drive = self.motivation_engine.get_dominant_drive()
        
        # Recupera pensamentos completos do histórico
        recent_thoughts_dicts = []
        for thought_id in self.thought_generator.thought_chain[-5:]:
            if thought_id in self.thought_generator.thoughts_history:
                thought = self.thought_generator.thoughts_history[thought_id]
                recent_thoughts_dicts.append(thought.to_dict())
            else:
                # Fallback se não encontrar no histórico
                recent_thoughts_dicts.append({
                    "id": thought_id,
                    "type": "unknown",
                    "content": "Pensamento registrado",
                    "importance": 0.5,
                    "confidence": 0.5,
                    "timestamp": datetime.now().isoformat(),
                    "acted_upon": False
                })
        
        return {
            "is_running": self.is_running,
            "last_external_input": self.last_external_input.isoformat() if self.last_external_input else None,
            "idle_seconds": (datetime.now() - self.last_external_input).total_seconds() if self.last_external_input else None,
            "dominant_drive": dominant_drive.type.value if dominant_drive else None,
            "drive_urgency": dominant_drive.get_urgency() if dominant_drive else 0,
            "meta_cognitive_state": {
                "cognitive_load": self.meta_cognition.state.cognitive_load,
                "focus_quality": self.meta_cognition.state.focus_quality,
                "fatigue_level": self.meta_cognition.state.fatigue_level,
                "flow_state": self.meta_cognition.state.flow_state
            },
            "autonomous_actions_count": len(self.autonomous_actions_log),
            "recent_thoughts": recent_thoughts_dicts
        }


# Factory function para criar sistema de autonomia completo
def create_autonomy_system(agent_core=None, memory_manager=None, conscience_engine=None) -> AutonomousThinkingLoop:
    """
    Cria sistema completo de autonomia
    
    Args:
        agent_core: Núcleo principal do agente
        memory_manager: Gerenciador de memória
        conscience_engine: Engine de consciência ética
    
    Returns:
        AutonomousThinkingLoop configurado
    """
    loop = AutonomousThinkingLoop(
        agent_core=agent_core,
        memory_manager=memory_manager,
        conscience_engine=conscience_engine
    )
    
    logger.info("Sistema de autonomia criado com sucesso")
    return loop
