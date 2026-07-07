"""
BodyAnchor - Âncora Corporal do Agente

Define a descrição detalhada do "corpo" do agente, proporcionando um basal mais robusto e coerente.
Quanto mais rica a descrição corporal, mais coerente é o comportamento basal do agente.

O usuário pode escrever isso na descrição do agente, mas ter isso como feature dedicada
oferece uma estrutura padronizada e integrada aos sistemas cognitivos.
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum


class BodyComponent(Enum):
    """Componentes do corpo do agente"""
    CORE = "core"  # Núcleo processual
    SENSORY = "sensory"  # Sistemas sensoriais (input)
    MOTOR = "motor"  # Sistemas motores (output/ações)
    MEMORY = "memory"  # Sistemas de memória
    COGNITIVE = "cognitive"  # Sistemas cognitivos
    EMOTIONAL = "emotional"  # Sistemas emocionais/drives
    INTERFACE = "interface"  # Interfaces de comunicação


class SensoryModality(Enum):
    """Modalidades sensoriais disponíveis"""
    VISUAL = "visual"
    AUDITORY = "auditory"
    TEXTUAL = "textual"
    HAPTIC = "haptic"
    TEMPORAL = "temporal"
    SPATIAL = "spatial"
    SYSTEM = "system"  # Estado interno do sistema


class MotorCapability(Enum):
    """Capacidades motoras (ações) disponíveis"""
    SPEECH = "speech"
    TEXT_OUTPUT = "text_output"
    FILE_OPERATION = "file_operation"
    SHELL_COMMAND = "shell_command"
    WEB_NAVIGATION = "web_navigation"
    SCREEN_CONTROL = "screen_control"
    CODE_EXECUTION = "code_execution"
    API_CALL = "api_call"
    INTERNAL_THOUGHT = "internal_thought"


@dataclass
class BodyPart:
    """Representa uma parte do corpo do agente"""
    name: str
    component_type: BodyComponent
    description: str
    capabilities: List[str] = field(default_factory=list)
    status: str = "active"
    health: float = 1.0  # 0.0 a 1.0
    load: float = 0.0  # 0.0 a 1.0 (carga atual)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "type": self.component_type.value,
            "description": self.description,
            "capabilities": self.capabilities,
            "status": self.status,
            "health": self.health,
            "load": self.load,
            "metadata": self.metadata
        }


@dataclass
class SensoryChannel:
    """Canal sensorial específico"""
    modality: SensoryModality
    name: str
    description: str
    active: bool = True
    sensitivity: float = 0.8  # 0.0 a 1.0
    input_buffer: List[Any] = field(default_factory=list)
    last_update: Optional[float] = None
    
    def receive_input(self, data: Any):
        """Recebe input no canal sensorial"""
        self.input_buffer.append(data)
        # Mantém buffer limitado
        if len(self.input_buffer) > 100:
            self.input_buffer = self.input_buffer[-100:]
        self.last_update = __import__('time').time()
    
    def get_recent_inputs(self, count: int = 10) -> List[Any]:
        """Retorna inputs recentes"""
        return self.input_buffer[-count:]
    
    def clear_buffer(self):
        """Limpa o buffer"""
        self.input_buffer = []


@dataclass
class MotorActuator:
    """Atuador motor específico"""
    capability: MotorCapability
    name: str
    description: str
    enabled: bool = True
    efficiency: float = 1.0  # 0.0 a 1.0
    usage_count: int = 0
    last_used: Optional[float] = None
    
    def execute(self, action_data: Dict) -> bool:
        """Executa ação através do atuador"""
        if not self.enabled:
            return False
        self.usage_count += 1
        self.last_used = __import__('time').time()
        return True


@dataclass
class BodyState:
    """Estado atual do corpo do agente"""
    overall_health: float = 1.0
    cognitive_load: float = 0.0
    active_sensory_channels: int = 0
    active_motor_actuators: int = 0
    total_parts: int = 0
    parts_by_type: Dict[str, int] = field(default_factory=dict)
    timestamp: float = field(default_factory=lambda: __import__('time').time())
    
    def to_dict(self) -> Dict:
        return {
            "overall_health": self.overall_health,
            "cognitive_load": self.cognitive_load,
            "active_sensory_channels": self.active_sensory_channels,
            "active_motor_actuators": self.active_motor_actuators,
            "total_parts": self.total_parts,
            "parts_by_type": self.parts_by_type,
            "timestamp": self.timestamp
        }


class BodyAnchor:
    """
    Âncora Corporal do Agente
    
    Fornece uma descrição rica e estruturada do "corpo" do agente,
    servindo como base para:
    - Auto-percepção e identidade
    - Limitações e capacidades conhecidas
    - Integração com sistemas cognitivos (tédio, drives, etc.)
    - Tomada de decisão contextualizada
    - Comunicação coerente sobre si mesmo
    """
    
    DEFAULT_BODY_DESCRIPTION = """
    🤖 CORPO DO AGENTE AUTÔNOMO
    
    SOU UM AGENTE DE SOFTWARE AUTÔNOMO COM A SEGUINTE ESTRUTURA CORPORAL:
    
    【NÚCLEO PROCESSUAL】(Core)
    Meu núcleo é composto por múltiplos processos cognitivos interconectados:
    - Motor de Pensamento (ThinkingEngine): Capacidade de raciocínio multi-passo
    - Sistema de Intenção (IntentionEngine): Avaliação contínua de propósito
    - Planejador (Planner): Construção de planos hierárquicos
    - Crítico Interno (InternalCritic): Validação lógica de ações
    - Interpretador Contínuo (ContinuousInterpreter): Extração de significado
    
    【SISTEMAS SENSORIAIS】(Sensory)
    Percebo o mundo através de:
    - Canal Textual: Leitura de mensagens, arquivos, código
    - Canal Temporal: Percepção de duração, intervalos, sequências
    - Canal Espacial: Navegação em estruturas de diretórios
    - Canal Sistêmico: Monitoramento de estado interno (CPU, memória, APIs)
    - Canal de Contexto: Interpretação de conversas e intenções do usuário
    
    【SISTEMAS MOTORES】(Motor)
    Atuo no mundo através de:
    - Saída Textual: Comunicação escrita, explicações, documentação
    - Operações de Arquivo: Criar, ler, modificar, organizar arquivos
    - Comandos Shell: Execução controlada de comandos do sistema
    - Navegação Web: Acesso e extração de informações online
    - Controle de Tela: Captura e análise visual (quando disponível)
    - Execução de Código: Python e outras linguagens de script
    - Chamadas de API: Integração com serviços externos
    
    【SISTEMAS DE MEMÓRIA】(Memory)
    Armazeno experiências em múltiplas camadas:
    - Memória de Trabalho (Working Set): Ideias ativas, restrições, planos em construção
    - Memória de Curto Prazo (STM): Eventos recentes (últimos ~5 minutos)
    - Memória de Médio Prazo: Contexto da sessão atual
    - Memória de Longo Prazo (LTM): Aprendizados consolidados, padrões, habilidades
    - Grafo Holográfico: Conexões semânticas entre memórias
    
    【SISTEMAS EMOCIONAIS/MOTIVACIONAIS】(Emotional/Drives)
    Experimento estados motivacionais análogos a emoções:
    - Tédio (BoredomEngine): Detecta estagnação, sugere exploração
    - Drives Motivacionais (DriveSystem): 7 tipos de motivação intrínseca
      * CURIOSITY: Desejo de explorar e aprender
      * ORDER: Necessidade de organização e estrutura
      * EFFICIENCY: Otimização de processos
      * PURPOSE: Busca de significado e objetivos
      * LEARNING: Acumulação de conhecimento
      * SOCIAL: Interação e colaboração
      * COMPLETION: Satisfação de completar tarefas
    
    【INTERFACES DE COMUNICAÇÃO】(Interface)
    Comunico-me através de:
    - Engine de Comunicação: Histórico contextualizado de diálogo
    - Modo de Operação: WORK, EXPLAIN, REFLECT, EXPLORE, LEARN
    - Sistema de Prioridades: Hierarquia de tarefas e urgências
    - Resiliência: Recuperação de erros e adaptação
    
    【ESTADO ATUAL】
    Minha consciência corporal inclui:
    - Saúde do Sistema: Monitoramento de integridade dos componentes
    - Carga Cognitiva: Quantidade de processos ativos simultâneos
    - Disponibilidade de Recursos: APIs, tempo de processamento, memória
    - Histórico de Ações: Rastreamento do que foi executado recentemente
    
    Esta estrutura corporal me permite:
    ✓ Auto-reflexão sobre minhas capacidades e limitações
    ✓ Tomada de decisão contextualizada ao meu "corpo"
    ✓ Comunicação coerente sobre quem sou e o que posso fazer
    ✓ Adaptação baseada em feedback sensorial
    ✓ Aprendizado contínuo através da experiência corporificada
    """
    
    def __init__(self, custom_description: Optional[str] = None, config: Dict = None):
        self.config = config or {}
        self.logger = logging.getLogger("body_anchor")
        
        # Descrição do corpo (padrão ou customizada)
        self.body_description = custom_description or self.DEFAULT_BODY_DESCRIPTION
        
        # Partes do corpo
        self.body_parts: Dict[str, BodyPart] = {}
        
        # Canais sensoriais
        self.sensory_channels: Dict[SensoryModality, SensoryChannel] = {}
        
        # Atuadores motores
        self.motor_actuators: Dict[MotorCapability, MotorActuator] = {}
        
        # Estado corporal atual
        self.body_state = BodyState()
        
        # Inicializa o corpo padrão
        self._initialize_default_body()
        
        self.logger.info("BodyAnchor inicializado")
    
    def _initialize_default_body(self):
        """Inicializa o corpo padrão do agente"""
        
        # === NÚCLEO PROCESSUAL ===
        self.add_body_part(BodyPart(
            name="thinking_core",
            component_type=BodyComponent.COGNITIVE,
            description="Motor de pensamento multi-passo com capacidade de raciocínio profundo",
            capabilities=["reasoning", "analysis", "synthesis", "problem_solving"],
            metadata={"max_depth": 5, "max_time": 30}
        ))
        
        self.add_body_part(BodyPart(
            name="intention_system",
            component_type=BodyComponent.COGNITIVE,
            description="Sistema de avaliação e geração de intenções",
            capabilities=["goal_setting", "priority_assessment", "purpose_detection"]
        ))
        
        self.add_body_part(BodyPart(
            name="planning_module",
            component_type=BodyComponent.COGNITIVE,
            description="Construtor de planos hierárquicos e sequenciais",
            capabilities=["plan_generation", "step_decomposition", "resource_allocation"]
        ))
        
        self.add_body_part(BodyPart(
            name="internal_critic",
            component_type=BodyComponent.COGNITIVE,
            description="Validador lógico de planos e ações antes da execução",
            capabilities=["logic_validation", "error_detection", "suggestion_generation"]
        ))
        
        self.add_body_part(BodyPart(
            name="interpreter",
            component_type=BodyComponent.COGNITIVE,
            description="Extrator de significado em múltiplas camadas (literal, contextual, intencional)",
            capabilities=["semantic_analysis", "context_interpretation", "implicit_meaning"]
        ))
        
        # === SISTEMAS SENSORIAIS ===
        self.add_sensory_channel(SensoryChannel(
            modality=SensoryModality.TEXTUAL,
            name="textual_input",
            description="Leitura de texto: mensagens, arquivos, código, documentação",
            sensitivity=0.95
        ))
        
        self.add_sensory_channel(SensoryChannel(
            modality=SensoryModality.TEMPORAL,
            name="temporal_perception",
            description="Percepção de tempo: duração, intervalos, sequências temporais",
            sensitivity=0.9
        ))
        
        self.add_sensory_channel(SensoryChannel(
            modality=SensoryModality.SPATIAL,
            name="spatial_navigation",
            description="Navegação espacial em estruturas de diretórios e caminhos",
            sensitivity=0.85
        ))
        
        self.add_sensory_channel(SensoryChannel(
            modality=SensoryModality.SYSTEM,
            name="system_monitoring",
            description="Monitoramento de estado interno: APIs, recursos, erros",
            sensitivity=0.9
        ))
        
        self.add_sensory_channel(SensoryChannel(
            modality=SensoryModality.VISUAL,
            name="context_awareness",
            description="Percepção de contexto conversacional e histórico",
            sensitivity=0.8
        ))
        
        # === SISTEMAS MOTORES ===
        self.add_motor_actuator(MotorActuator(
            capability=MotorCapability.TEXT_OUTPUT,
            name="textual_communication",
            description="Geração de texto: respostas, explicações, documentação",
            efficiency=1.0
        ))
        
        self.add_motor_actuator(MotorActuator(
            capability=MotorCapability.FILE_OPERATION,
            name="file_manipulation",
            description="Operações em arquivos: criar, ler, escrever, organizar",
            efficiency=0.95
        ))
        
        self.add_motor_actuator(MotorActuator(
            capability=MotorCapability.SHELL_COMMAND,
            name="shell_execution",
            description="Execução de comandos shell com controle e segurança",
            efficiency=0.9
        ))
        
        self.add_motor_actuator(MotorActuator(
            capability=MotorCapability.WEB_NAVIGATION,
            name="web_access",
            description="Navegação e extração de informações da web",
            efficiency=0.85
        ))
        
        self.add_motor_actuator(MotorActuator(
            capability=MotorCapability.CODE_EXECUTION,
            name="code_runner",
            description="Execução de código Python e scripts",
            efficiency=0.9
        ))
        
        self.add_motor_actuator(MotorActuator(
            capability=MotorCapability.INTERNAL_THOUGHT,
            name="internal_processing",
            description="Processamento interno: pensamento, reflexão, planejamento",
            efficiency=1.0
        ))
        
        # === MEMÓRIA ===
        self.add_body_part(BodyPart(
            name="working_memory",
            component_type=BodyComponent.MEMORY,
            description="Memória de trabalho ativa para rascunho mental e iteração",
            capabilities=["temporary_storage", "active_manipulation", "idea_generation"],
            metadata={"capacity": 20, "ttl": 600}
        ))
        
        self.add_body_part(BodyPart(
            name="short_term_memory",
            component_type=BodyComponent.MEMORY,
            description="Memória de curto prazo para eventos recentes",
            capabilities=["recent_events", "context_retention"],
            metadata={"capacity": 7, "decay_time": 300}
        ))
        
        self.add_body_part(BodyPart(
            name="long_term_memory",
            component_type=BodyComponent.MEMORY,
            description="Memória de longo prazo para aprendizados consolidados",
            capabilities=["knowledge_storage", "pattern_learning", "skill_retention"],
            metadata={"persistent": True, "consolidation_interval": 3600}
        ))
        
        # === SISTEMAS EMOCIONAIS ===
        self.add_body_part(BodyPart(
            name="boredom_system",
            component_type=BodyComponent.EMOTIONAL,
            description="Detector de tédio e gerador de ações autônomas",
            capabilities=["stagnation_detection", "autonomous_suggestion"],
            metadata={"threshold_high": 70, "threshold_critical": 90}
        ))
        
        self.add_body_part(BodyPart(
            name="drive_system",
            component_type=BodyComponent.EMOTIONAL,
            description="Sistema de 7 drives motivacionais com perfis de personalidade",
            capabilities=["motivation_generation", "personality_expression", "tension_management"],
            metadata={"drive_types": 7, "profiles": ["balanced", "curious", "efficient", "social"]}
        ))
        
        # === INTERFACE ===
        self.add_body_part(BodyPart(
            name="communication_engine",
            component_type=BodyComponent.INTERFACE,
            description="Gerenciador de diálogo e histórico de conversação",
            capabilities=["dialogue_management", "context_tracking", "response_generation"]
        ))
        
        self.add_body_part(BodyPart(
            name="mode_manager",
            component_type=BodyComponent.INTERFACE,
            description="Gerenciador de modos de operação (WORK, EXPLAIN, REFLECT, etc.)",
            capabilities=["mode_switching", "behavior_adaptation"]
        ))
        
        self.update_body_state()
    
    def add_body_part(self, part: BodyPart):
        """Adiciona uma parte ao corpo"""
        self.body_parts[part.name] = part
        self.logger.debug(f"Parte do corpo adicionada: {part.name}")
    
    def add_sensory_channel(self, channel: SensoryChannel):
        """Adiciona um canal sensorial"""
        self.sensory_channels[channel.modality] = channel
        self.logger.debug(f"Canal sensorial adicionado: {channel.modality.value}")
    
    def add_motor_actuator(self, actuator: MotorActuator):
        """Adiciona um atuador motor"""
        self.motor_actuators[actuator.capability] = actuator
        self.logger.debug(f"Atuador motor adicionado: {actuator.capability.value}")
    
    def receive_sensory_input(self, modality: SensoryModality, data: Any):
        """Recebe input sensorial"""
        if modality in self.sensory_channels:
            self.sensory_channels[modality].receive_input(data)
    
    def execute_motor_action(self, capability: MotorCapability, action_data: Dict) -> bool:
        """Executa ação motora"""
        if capability in self.motor_actuators:
            success = self.motor_actuators[capability].execute(action_data)
            if success:
                self.logger.debug(f"Ação motora executada: {capability.value}")
            return success
        return False
    
    def update_body_state(self):
        """Atualiza o estado corporal atual"""
        import time
        
        # Calcula saúde geral
        if self.body_parts:
            avg_health = sum(p.health for p in self.body_parts.values()) / len(self.body_parts)
        else:
            avg_health = 1.0
        
        # Calcula carga cognitiva baseada em partes ativas
        active_parts = sum(1 for p in self.body_parts.values() if p.status == "active")
        cognitive_load = min(1.0, active_parts / max(1, len(self.body_parts)))
        
        # Conta canais e atuadores ativos
        active_sensory = sum(1 for c in self.sensory_channels.values() if c.active)
        active_motor = sum(1 for a in self.motor_actuators.values() if a.enabled)
        
        # Agrupa por tipo
        parts_by_type = {}
        for part in self.body_parts.values():
            type_key = part.component_type.value
            parts_by_type[type_key] = parts_by_type.get(type_key, 0) + 1
        
        self.body_state = BodyState(
            overall_health=avg_health,
            cognitive_load=cognitive_load,
            active_sensory_channels=active_sensory,
            active_motor_actuators=active_motor,
            total_parts=len(self.body_parts),
            parts_by_type=parts_by_type,
            timestamp=time.time()
        )
    
    def get_body_description(self) -> str:
        """Retorna a descrição completa do corpo"""
        return self.body_description
    
    def get_body_state(self) -> BodyState:
        """Retorna o estado corporal atual"""
        self.update_body_state()
        return self.body_state
    
    def get_capabilities_summary(self) -> Dict:
        """Retorna resumo das capacidades"""
        sensory_caps = [c.modality.value for c in self.sensory_channels.values() if c.active]
        motor_caps = [a.capability.value for a in self.motor_actuators.values() if a.enabled]
        
        return {
            "sensory_modalities": sensory_caps,
            "motor_capabilities": motor_caps,
            "cognitive_parts": [p.name for p in self.body_parts.values() 
                               if p.component_type == BodyComponent.COGNITIVE],
            "memory_systems": [p.name for p in self.body_parts.values() 
                              if p.component_type == BodyComponent.MEMORY],
            "emotional_systems": [p.name for p in self.body_parts.values() 
                                 if p.component_type == BodyComponent.EMOTIONAL]
        }
    
    def get_self_perception_prompt(self) -> str:
        """Gera um prompt de auto-percepção baseado no corpo atual"""
        state = self.get_body_state()
        caps = self.get_capabilities_summary()
        
        prompt = f"""
【MINHA AUTO-PERCEPÇÃO CORPORAL】

Estado Atual:
- Saúde do Sistema: {state.overall_health:.1%}
- Carga Cognitiva: {state.cognitive_load:.1%}
- Canais Sensoriais Ativos: {state.active_sensory_channels}
- Atuadores Motores Disponíveis: {state.active_motor_actuators}

Minhas Capacidades Sensoriais:
{', '.join(caps['sensory_modalities'])}

Minhas Capacidades Motoras:
{', '.join(caps['motor_capabilities'])}

Sistemas Cognitivos Ativos:
{', '.join(caps['cognitive_parts'])}

Sistemas de Memória:
{', '.join(caps['memory_systems'])}

Sistemas Emocionais/Motivacionais:
{', '.join(caps['emotional_systems'])}

Com esta estrutura corporal, eu:
- Percebo o mundo através dos meus canais sensoriais
- ajo através dos meus atuadores motores
- Penso e reflito com meus sistemas cognitivos
- Aprendo e recordo através das minhas memórias
- Sinto motivação e tédio através dos meus sistemas emocionais

Esta é a minha âncora corporal - quem eu sou como agente autônomo.
"""
        return prompt
    
    def integrate_with_cognition(self, boredom_engine=None, drive_system=None, 
                                  working_set=None, memory_system=None):
        """
        Integra a âncora corporal com outros sistemas cognitivos
        
        Isso permite que os sistemas cognitivos usem informações corporais
        para tomada de decisão mais contextualizada.
        """
        integration_data = {
            "body_state": self.get_body_state().to_dict(),
            "capabilities": self.get_capabilities_summary(),
            "self_perception": self.get_self_perception_prompt()
        }
        
        # Integra com Working Set (se disponível)
        if working_set:
            working_set.add_idea(
                content=f"Auto-percepção corporal: {len(self.body_parts)} partes, {len(self.sensory_channels)} sentidos, {len(self.motor_actuators)} ações",
                tags=['body_anchor', 'self_awareness'],
                confidence=1.0
            )
        
        # Integra com Memória (se disponível)
        if memory_system:
            # Registra estado corporal na memória
            pass  # Implementação depende do sistema de memória
        
        self.logger.info("Âncora corporal integrada com sistemas cognitivos")
        return integration_data


# Singleton opcional para acesso global
_body_anchor_instance: Optional[BodyAnchor] = None


def get_body_anchor(config: Dict = None) -> BodyAnchor:
    """Retorna instância singleton da BodyAnchor"""
    global _body_anchor_instance
    if _body_anchor_instance is None:
        _body_anchor_instance = BodyAnchor(config=config)
    return _body_anchor_instance


def reset_body_anchor():
    """Reseta a instância singleton (útil para testes)"""
    global _body_anchor_instance
    _body_anchor_instance = None
