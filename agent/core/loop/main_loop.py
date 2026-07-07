"""
Main Loop - Loop principal do agente autônomo

Integra todos os componentes:
- Estado
- Cognição (intenção, pensamento, planejamento, tédio, drives, crítico, interpretação, working set)
- Gatilhos
- Modos
- Prioridades
- Reflexão
- Alinhamento Ético (Alignment Engine)
- Resiliência
- Memória (curto, médio e longo prazo)
"""

import time
import logging
from datetime import datetime
from typing import Optional, Dict, Any

# Importa componentes do núcleo
from agent.core.state.agent_state import StateManager, AgentState, AgentMode, Task
from agent.core.state.context_manager import ContextManager
from agent.core.cognition.intention import IntentionEngine, IntentionType
from agent.core.cognition.thinking import ThinkingEngine
from agent.core.cognition.planner import Planner
from agent.core.cognition.reflection import ReflectionEngine
from agent.core.cognition.communication import CommunicationEngine
from agent.core.cognition.boredom import BoredomEngine, BoredomAction
from agent.core.cognition.drive import DriveSystem, DriveType
from agent.core.cognition.critic import InternalCritic
from agent.core.cognition.interpretation import ContinuousInterpreter, RawInput
from agent.core.cognition.working_set import WorkingMemorySet
from agent.core.autonomy.mode_manager import ModeManager, Mode
from agent.core.autonomy.priorities import PriorityManager
from agent.core.autonomy.triggers import TriggerManager
from agent.core.autonomy.resilience import ResilienceManager, ErrorContext, ErrorSeverity

# Importa Alignment Engine para verificação ética
from agent.safety.alignment import AlignmentEngine, AlignmentConfig

# Importa sistema de memória
from agent.memory.manager import HolographicMemoryGraph, MemoryNode, MemoryType, MemoryConsolidation
from agent.memory.short_term import ShortTermMemory
from agent.memory.long_term import LongTermMemory


class AgentLoop:
    """
    Loop principal do agente autônomo
    
    Executa continuamente:
    1. Observar estado interno e externo
    2. Verificar consumo e disponibilidade de APIs
    3. Checar tarefas do usuário
    4. Avaliar gatilhos
    5. Definir intenção
    6. Planejar ação
    7. Verificar alinhamento ético (Alignment)
    8. Executar (quando aprovado)
    9. Registrar
    10. Refletir
    11. Aguardar próximo ciclo
    """
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        
        # Inicializa componentes
        self.state_manager = StateManager()
        self.context_manager = ContextManager(
            max_size=self.config.get("max_context_size", 50)
        )
        self.intention_engine = IntentionEngine()
        self.thinking_engine = ThinkingEngine(
            max_depth=self.config.get("max_thinking_depth", 5),
            max_time=self.config.get("max_reasoning_time", 30)
        )
        self.planner = Planner()
        self.reflection_engine = ReflectionEngine()
        self.communication_engine = CommunicationEngine()
        self.mode_manager = ModeManager(
            initial_mode=Mode[self.config.get("initial_mode", "WORK").upper()]
        )
        self.priority_manager = PriorityManager()
        self.trigger_manager = TriggerManager()
        
        # Inicializa sistemas cognitivos desconectados
        self.boredom_engine = BoredomEngine()
        self.drive_system = DriveSystem(
            personality_profile=self.config.get("personality_profile", "balanced")
        )
        self.internal_critic = InternalCritic()
        self.interpreter = ContinuousInterpreter()
        self.working_set = WorkingMemorySet(
            max_items=self.config.get("max_working_items", 20),
            ttl_seconds=self.config.get("working_set_ttl", 600)
        )
        
        # Inicializa sistema de resiliência
        self.resilience_manager = ResilienceManager()
        
        # Inicializa sistema de memória (curto, médio e longo prazo)
        self.short_term_memory = ShortTermMemory(
            capacity=self.config.get("stm_capacity", 7),
            decay_time=self.config.get("stm_decay_time", 300)
        )
        self.long_term_memory = LongTermMemory(
            storage_path=self.config.get("ltm_storage_path", "/workspace/agent/memory/ltm_store"),
            consolidation_interval=self.config.get("consolidation_interval", 3600)
        )
        self.memory_graph = HolographicMemoryGraph()
        
        # Inicializa Alignment Engine com constituição customizada
        constitution_path = self.config.get(
            "constitution_path",
            "/workspace/agent/safety/custom_constitution.yaml"
        )
        alignment_config = AlignmentConfig(
            auto_reject_critical_violations=self.config.get("auto_reject_critical", True),
            log_all_deliberations=self.config.get("log_deliberations", True),
            require_high_confidence=self.config.get("require_high_confidence", False),
            minimum_confidence_threshold=self.config.get("min_confidence_threshold", 0.7)
        )
        self.alignment_engine = AlignmentEngine(
            constitution_path=constitution_path,
            config=alignment_config
        )
        
        # Configuração do loop
        self.base_interval = self.config.get("base_loop_interval", 5)
        self.running = False
        self.cycle_count = 0
        
        # Setup logging
        self.logger = self._setup_logging()
        
        # Callbacks (serão implementados com ferramentas reais)
        self.action_executor = None
        self.llm_client = None
    
    def _setup_logging(self) -> logging.Logger:
        """Configura logging"""
        logger = logging.getLogger("agent_loop")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def set_action_executor(self, executor):
        """Define executor de ações (injeção de dependência)"""
        self.action_executor = executor
    
    def set_llm_client(self, client):
        """Define cliente LLM (injeção de dependência)"""
        self.llm_client = client
    
    def add_user_task(self, description: str, priority: int = 5):
        """Adiciona tarefa do usuário e registra na comunicação"""
        task_id = f"user_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Adiciona ao state manager
        task = Task(
            id=task_id,
            description=description,
            priority=priority,
            source="user"
        )
        self.state_manager.add_task(task)
        
        # Adiciona ao priority manager
        self.priority_manager.add_task(
            task_id=task_id,
            description=description,
            source="USER",
            level="NORMAL" if priority <= 5 else "HIGH",
            metadata={"source": "user"}
        )
        
        # Registra no histórico de conversação
        self.communication_engine.add_user_message(
            content=description,
            metadata={"task_id": task_id, "priority": priority}
        )
        
        # Força modo trabalho
        self.mode_manager.force_work_mode("Tarefa do usuário adicionada")
        
        # Sinaliza evento
        self.trigger_manager.signal_event("user_task_added")
        
        self.logger.info(f"Tarefa do usuário adicionada: {description}")
        return task_id
    
    def _observe(self) -> Dict[str, Any]:
        """Fase 1: Observar estado interno e externo"""
        self.state_manager.set_state(AgentState.IDLE)
        
        status = self.state_manager.get_status()
        idle_time = self.state_manager.get_idle_time()
        
        # Atualiza sistemas cognitivos (tédio e drives)
        boredom_state = self.boredom_engine.update(
            has_user_tasks=self.priority_manager.has_user_tasks(),
            is_executing=(status.state == AgentState.EXECUTING),
            recent_discoveries=0  # Pode ser incrementado com descobertas reais
        )
        
        drive_state = self.drive_system.update(
            recent_actions=[],
            environment_changes=0,
            user_interactions=1 if self.trigger_manager.was_event_signaled("user_task_added") else 0,
            completed_tasks=0
        )
        
        return {
            "state": status.state,
            "mode": status.mode,
            "idle_time": idle_time,
            "has_user_tasks": self.priority_manager.has_user_tasks(),
            "cycle_count": self.cycle_count,
            "errors_in_cycle": status.errors_in_cycle,
            "llm_calls_in_cycle": status.llm_calls_in_cycle,
            "context_summary": self.context_manager.get_summary(),
            "boredom_level": boredom_state.level.value,
            "boredom_score": boredom_state.score,
            "dominant_drive": drive_state.dominant_drive.value if drive_state.dominant_drive else None,
            "motivational_tension": drive_state.overall_tension
        }
    
    def _check_triggers(self) -> list:
        """Fase 2-4: Verificar gatilhos"""
        active_triggers = self.trigger_manager.get_active_triggers()
        
        for trigger in active_triggers:
            self.logger.debug(f"Gatilho ativo: {trigger.id} ({trigger.description})")
            self.trigger_manager.fire_trigger(trigger.id)
        
        return active_triggers
    
    def _determine_intention(self, observation: Dict) -> IntentionType:
        """Fase 5: Definir intenção"""
        mode_value = observation["mode"].value if hasattr(observation["mode"], 'value') else observation["mode"]
        
        # Verifica sugestões do sistema de tédio e drives
        boredom_action = self.boredom_engine.get_suggested_action()
        drive_suggestions = self.drive_system.get_action_suggestions()
        
        # Se tédio alto sugere ação autônoma
        if boredom_action and observation["boredom_score"] > 60:
            self.logger.info(f"🎯 Tédio sugere ação: {boredom_action.value}")
            # Mapeia ação de tédio para intenção
            boredom_to_intention = {
                BoredomAction.EXPLORE: IntentionType.EXPLORE,
                BoredomAction.LEARN: IntentionType.LEARN,
                BoredomAction.REFLECT: IntentionType.REFLECT,
                BoredomAction.ASK_USER: IntentionType.ACT
            }
            if boredom_action in boredom_to_intention:
                intention_type = boredom_to_intention[boredom_action]
                self.context_manager.set_intention(f"{intention_type.value} (tédio)")
                self.logger.info(f"Intenção determinada por tédio: {intention_type.value}")
                return intention_type
        
        # Se drives tensionados sugerem ação
        if drive_suggestions and observation.get("motivational_tension", 0) > 30:
            for suggestion in drive_suggestions[:1]:  # Pega o mais prioritário
                self.logger.info(f"💡 Drive sugere: {suggestion['recommended_action']}")
        
        intention = self.intention_engine.evaluate(
            has_user_tasks=observation["has_user_tasks"],
            idle_time=observation["idle_time"],
            mode=mode_value,
            context_summary=observation.get("context_summary"),
            errors_recent=observation["errors_in_cycle"],
            llm_calls_recent=observation["llm_calls_in_cycle"],
            max_llm_calls=self.config.get("max_llm_calls_per_cycle", 3)
        )
        
        self.context_manager.set_intention(intention.intention_type.value)
        self.logger.info(f"Intenção determinada: {intention.intention_type.value} - {intention.reason}")
        
        return intention.intention_type
    
    def _think(self, intention: IntentionType) -> Optional[str]:
        """Fase 6: Pensar sobre a ação (interno, não exposto)."""
        # Interpreta o contexto antes de pensar
        raw_input = RawInput(
            source="internal",
            content_type="text",
            raw_data=f"Intenção atual: {intention.value}",
            context_snapshot={"mode": self.mode_manager.get_mode().value}
        )
        interpretations = self.interpreter.interpret(raw_input)
        
        # Registra interpretação de maior confiança
        if interpretations:
            best_interp = interpretations[0]
            self.logger.debug(f"Interpretação: {best_interp.content} (confiança: {best_interp.confidence:.2f})")
            for implicit in best_interp.implicit_meanings:
                self.context_manager.add_thought(f"[IMPLÍCITO] {implicit}")
        
        if intention == IntentionType.NO_ACT:
            # Mesmo em NO_ACT, pode haver pensamento espontâneo
            thought = self.thinking_engine.spontaneous_thought()
            if thought:
                self.logger.info(f"🧠 Pensamento autônomo gerado: {thought.conclusion}")
                # Adiciona ao working set como ideia espontânea
                self.working_set.add_idea(
                    content=thought.conclusion,
                    tags=['spontaneous', 'autonomous'],
                    confidence=thought.confidence
                )
                # Registra no contexto interno
                for step in thought.steps:
                    self.context_manager.add_thought(f"[AUTÔNOMO] {step.content}")
            return None
        
        if intention == IntentionType.WAIT:
            # Mesmo em WAIT, pode haver pensamento espontâneo
            thought = self.thinking_engine.spontaneous_thought()
            if thought:
                self.logger.info(f"🧠 Pensamento autônomo gerado: {thought.conclusion}")
                # Adiciona ao working set
                self.working_set.add_idea(
                    content=thought.conclusion,
                    tags=['spontaneous', 'wait'],
                    confidence=thought.confidence
                )
                # Registra no contexto interno
                for step in thought.steps:
                    self.context_manager.add_thought(f"[AUTÔNOMO] {step.content}")
            return None
        
        # Inicia processo de pensamento REATIVO usando working set
        question = f"Como proceder com intenção: {intention.value}?"
        self.thinking_engine.start_thinking(question)
        
        # Adiciona restrições ao working set
        self.working_set.add_constraint(
            f"Modo atual: {self.mode_manager.get_mode().value}",
            severity='medium'
        )
        
        # Adiciona passos de pensamento (simplificado)
        self.thinking_engine.add_thought_step(
            f"Avaliando contexto atual...",
            confidence=0.9
        )
        
        # Conclusão baseada na intenção
        action_map = {
            IntentionType.ACT: "Executar tarefa pendente",
            IntentionType.EXPLORE: "Explorar contexto em busca de aprendizado",
            IntentionType.LEARN: "Organizar memória e extrair padrões",
            IntentionType.REFLECT: "Analisar ações recentes"
        }
        
        action = action_map.get(intention, "Aguardar")
        
        process = self.thinking_engine.conclude(
            conclusion=f"Ação recomendada: {action}",
            action=action,
            confidence=0.8
        )
        
        # Promove ideias de alta confiança do working set
        for item in self.working_set.get_active_items():
            if item.confidence >= 0.7:
                self.working_set.promote_item(item.id)
        
        # Exporta working set para uso no planejamento
        working_export = self.working_set.export_for_planning()
        if working_export['promoted_items'] or working_export['high_confidence_ideas']:
            self.logger.info(f"Working Set: {len(working_export['promoted_items'])} itens promovidos, {len(working_export['high_confidence_ideas'])} de alta confiança")
        
        # Registra pensamentos no contexto (INTERNO - não exposto ao usuário)
        for step in process.steps:
            self.context_manager.add_thought(step.content)
        
        self.logger.debug(f"Pensamento interno concluído: {process.conclusion}")
        return action
    
    def _plan(self, action: str) -> bool:
        """Fase 7: Planejar ação"""
        if not action:
            return False
        
        plan = self.planner.create_plan(action)
        
        # Valida plano com InternalCritic antes de aprovar
        plan_dict = {
            "id": f"plan_{self.cycle_count}",
            "goal": action,
            "actions": [{"id": step.id, "name": step.description, "description": step.description} for step in plan.steps],
            "required_resources": [],
            "estimated_time_seconds": len(plan.steps) * 30,
            "fallback_plan": None
        }
        
        context = {
            "available_resources": ["filesystem", "web", "shell"],
            "max_execution_time_seconds": 300,
            "agent_mode": self.mode_manager.get_mode().value
        }
        
        critique_report = self.internal_critic.evaluate_plan(plan_dict, context)
        
        if not critique_report.is_approved:
            critical_issues = critique_report.get_critical_issues()
            self.logger.warning(f"❌ Plano reprovado pelo crítico: {len(critical_issues)} issues críticos")
            for issue in critical_issues:
                self.logger.warning(f"   - {issue.issue}: {issue.suggestion}")
            # Tenta corrigir o plano ou criar alternativo
            return False
        
        if critique_report.critiques:
            self.logger.info(f"✅ Plano aprovado com {len(critique_report.critiques)} observações")
        
        self.context_manager.set_plan([step.description for step in plan.steps])
        
        # Armazena no working set como hipótese promovida
        self.working_set.add_idea(
            content=f"Plano: {action}",
            tags=['plan', 'approved'],
            confidence=critique_report.overall_confidence
        )
        
        self.logger.info(f"Plano criado: {action} ({len(plan.steps)} etapas)")
        return True
    
    def _check_alignment(self, action_description: str, context: Dict = None) -> bool:
        """
        Fase intermediária: Verificar alinhamento ético da ação
        
        Returns:
            bool: True se ação está aprovada, False se rejeitada
        """
        if not hasattr(self, 'alignment_engine'):
            # Se alignment engine não estiver disponível, permite execução
            self.logger.warning("Alignment Engine não disponível, pulando verificação ética")
            return True
        
        try:
            result = self.alignment_engine.check_action(
                action_description=action_description,
                context=context or {},
                stakeholders=["usuário"],
                urgency=0.5,
                reversibility=0.8
            )
            
            # Log da deliberação
            self.logger.info(
                f"🛡️ Alignment Check: {result.deliberation.outcome.value} - "
                f"Confiança: {result.deliberation.confidence:.2f}"
            )
            
            if result.deliberation.reasoning:
                self.logger.debug(f"Raciocínio ético: {result.deliberation.reasoning}")
            
            # Registra no contexto se houver princípios invocados
            if result.deliberation.principles_invoked:
                self.context_manager.add_thought(
                    f"[ALIGNMENT] Princípios: {', '.join(result.deliberation.principles_invoked)}"
                )
            
            return result.approved
            
        except Exception as e:
            self.logger.error(f"Erro na verificação de alignment: {e}")
            # Em caso de erro, segue princípio da precaução
            return False
    
    def _execute(self) -> bool:
        """Fase 8: Executar ação e gerar resposta ao usuário usando executor real"""
        plan = self.planner.get_current_plan()
        if not plan:
            return False
        
        step = self.planner.get_next_step()
        if not step:
            return True  # Plano completo
        
        # VERIFICAÇÃO DE ALIGNMENT ANTES DA EXECUÇÃO
        alignment_context = {
            "mode": self.mode_manager.get_mode().value,
            "state": AgentState.EXECUTING.value,
            "plan_intention": plan.intention,
            "step_id": step.id
        }
        
        if not self._check_alignment(step.description, alignment_context):
            self.logger.warning(
                f"⛔ Ação bloqueada por alinhamento ético: {step.description}"
            )
            self.planner.fail_step(step.id, "Ação não aprovada pelo Alignment Engine")
            self.state_manager.set_state(AgentState.IDLE)
            return False
        
        self.state_manager.set_state(AgentState.EXECUTING)
        
        try:
            # Usa ActionExecutor real em vez de simulação
            from core.loop.action_executor import get_executor
            
            executor = get_executor()
            
            # Mapeia intenção para tipo de ação
            action_type_map = {
                "Executar tarefa pendente": "file_operation",
                "Explorar contexto em busca de aprendizado": "web_search",
                "Organizar memória e extrair padrões": "log_insight",
                "Analisar ações recentes": "code_analysis"
            }
            
            action_type = action_type_map.get(plan.intention, "generic")
            
            # Executa ação real
            result = executor.execute_action(
                action_type=action_type,
                description=step.description,
                context={
                    "mode": self.mode_manager.get_mode().value,
                    "state": AgentState.EXECUTING.value,
                    "plan_intention": plan.intention,
                    "alignment_approved": True
                },
                plan_step={"id": step.id, "description": step.description}
            )
            
            if result.success:
                self.planner.complete_step(step.id, str(result.result))
                
                # Adiciona resultado ao contexto
                self.context_manager.add_item(
                    f"{result.description}: {str(result.result)[:500]}",
                    "assistant",
                    {"step": step.id, "tool_used": result.tool_used, "tokens_used": result.tokens_used}
                )
                
                # Gera resposta ao usuário baseada na execução real
                context = {
                    "mode": self.mode_manager.get_mode().value,
                    "state": AgentState.EXECUTING.value
                }
                response = self.communication_engine.generate_response(
                    thought_conclusion=f"Tarefa concluída: {result.description}",
                    action_taken=result.description,
                    context=context
                )
                
                # Log da resposta
                if response.content:
                    self.logger.info(f"Resposta ao usuário: {response.content}")
                
                self.logger.info(f"Etapa executada com sucesso: {step.description} (ferramenta: {result.tool_used})")
                return True
            else:
                # Falha na execução
                self.planner.fail_step(step.id, result.error or "Erro desconhecido")
                self.state_manager.increment_error()
                self.logger.error(f"Falha na execução: {result.error}")
                return False
            
        except Exception as e:
            self.planner.fail_step(step.id, str(e))
            self.state_manager.increment_error()
            self.logger.error(f"Erro na execução: {e}")
            return False
    
    def _reflect(self):
        """Fase 9: Refletir sobre ações"""
        if not self.config.get("enable_reflection", True):
            return
        
        plan = self.planner.get_current_plan()
        if not plan or plan.status != "completed":
            return
        
        # Cria reflexão sobre o plano completado
        reflection = self.reflection_engine.create_reflection(
            action=plan.intention,
            expected="Execução bem-sucedida",
            actual="Plano completado",
            confidence_before=0.8
        )
        
        self.logger.info(f"Reflexão criada: {len(reflection.lessons_learned)} lições aprendidas")
        
        # Consolida reflexão na memória de longo prazo
        for lesson in reflection.lessons_learned:
            # Adiciona à memória de longo prazo
            self.long_term_memory.store(
                content=f"Liçao aprendida: {lesson}",
                memory_type="semantic",
                tags=['reflection', 'lesson_learned'],
                importance=0.7
            )
            
            # Cria nodo no grafo holográfico
            node = MemoryNode(
                content=lesson,
                memory_type=MemoryType.SEMANTIC,
                consolidation_state=MemoryConsolidation.CONSOLIDATED,
                source="reflection",
                importance_score=0.7,
                tags={'reflection', 'lesson'}
            )
            self.memory_graph.add_memory(node)
        
        # Satisfaz drives de learning e completion
        self.drive_system.satisfy_drive(DriveType.LEARNING, amount=15.0)
        self.drive_system.satisfy_drive(DriveType.COMPLETION, amount=20.0)
        
        # Reduz tédio após reflexão produtiva
        self.boredom_engine.record_stimulation(
            event_type="self_initiated",
            description="Reflexão completada",
            impact=15.0
        )
    
    def _register(self):
        """Fase 10: Registrar ciclo"""
        self.cycle_count += 1
        self.state_manager.increment_cycle()
        self.state_manager.update_last_action()
        
        # Limpa working set descartados periodicamente
        if self.cycle_count % 5 == 0:
            self.working_set.clear_discarded()
        
        # Consolidação periódica da memória (a cada 10 ciclos)
        if self.cycle_count % 10 == 0:
            self._consolidate_memories()
    
    def _consolidate_memories(self):
        """Consolida memórias de curto prazo para longo prazo"""
        # Recupera itens da memória de curto prazo
        stm_items = self.short_term_memory.get_all()
        
        for item in stm_items:
            # Itens com alta importância vão para LTM
            if hasattr(item, 'importance') and item.importance > 0.6:
                # Cria nodo no grafo holográfico
                node = MemoryNode(
                    content=str(item),
                    memory_type=MemoryType.SEMANTIC,
                    consolidation_state=MemoryConsolidation.CONSOLIDATED,
                    source="short_term_consolidation",
                    importance_score=item.importance if hasattr(item, 'importance') else 0.5
                )
                self.memory_graph.add_memory(node)
                
                # Remove da STM após consolidação
                self.short_term_memory.forget(item)
        
        # Reseta working set a cada consolidação
        self.working_set.reset()
        
        self.logger.debug("Consolidação de memórias completada")
    
    def run_cycle(self) -> Dict:
        """Executa um ciclo completo"""
        self.logger.debug(f"Iniciando ciclo {self.cycle_count + 1}")
        
        try:
            # Fase 1: Observar
            observation = self._observe()
            
            # Fase 2-4: Verificar gatilhos
            triggers = self._check_triggers()
            
            # Fase 5: Determinar intenção
            intention = self._determine_intention(observation)
            
            # Fase 6: Pensar
            action = self._think(intention)
            
            # Fase 7: Planejar
            if action:
                self._plan(action)
                
                # Fase 8: Executar
                self._execute()
                
                # Fase 9: Refletir
                self._reflect()
            
            # Fase 10: Registrar
            self._register()
            
            # Atualiza modo se necessário
            self.mode_manager.evaluate_transitions(
                has_user_tasks=observation["has_user_tasks"],
                idle_time=observation["idle_time"],
                error_rate=0.0  # Calcular baseado em histórico
            )
            
            # Retorna para modo idle
            self.state_manager.set_state(AgentState.IDLE)
            
            return {
                "cycle": self.cycle_count,
                "intention": intention.value,
                "action": action,
                "triggers": [t.id for t in triggers],
                "mode": self.mode_manager.get_mode().value
            }
            
        except Exception as e:
            self.logger.error(f"Erro no ciclo: {e}")
            self.state_manager.increment_error()
            self.state_manager.set_state(AgentState.IDLE)
            
            return {
                "cycle": self.cycle_count,
                "error": str(e)
            }
    
    def run_continuous(self, max_cycles: int = None):
        """Executa loop contínuo"""
        self.running = True
        cycles_run = 0
        
        self.logger.info("Iniciando loop contínuo do agente")
        self.logger.info(f"Modo inicial: {self.mode_manager.get_mode().value}")
        self.logger.info(f"Intervalo base: {self.base_interval}s")
        
        try:
            while self.running:
                result = self.run_cycle()
                cycles_run += 1
                
                self.logger.info(f"Ciclo {cycles_run}: {result.get('intention', 'unknown')}")
                
                # Verifica limite de ciclos
                if max_cycles and cycles_run >= max_cycles:
                    self.logger.info(f"Limite de {max_cycles} ciclos atingido")
                    break
                
                # Aguarda próximo ciclo
                time.sleep(self.base_interval)
                
        except KeyboardInterrupt:
            self.logger.info("Interrupto pelo usuário")
        finally:
            self.stop()
    
    def stop(self):
        """Para o loop"""
        self.running = False
        self.logger.info("Loop parado")
    
    def get_status(self) -> Dict:
        """Retorna status completo do agente"""
        return {
            "running": self.running,
            "cycle_count": self.cycle_count,
            "mode": self.mode_manager.get_mode().value,
            "state": self.state_manager.get_status().state.value,
            "priority_stats": self.priority_manager.get_statistics(),
            "trigger_stats": self.trigger_manager.get_statistics(),
            "reflection_stats": self.reflection_engine.get_summary(),
            "thinking_stats": self.thinking_engine.get_summary(),
            "planning_stats": self.planner.get_summary(),
            "communication_stats": {
                "messages_in_history": len(self.communication_engine.conversation_history),
                "last_response_tone": self.communication_engine.current_response.tone if self.communication_engine.current_response else None
            },
            # Novos sistemas cognitivos
            "boredom_stats": self.boredom_engine.get_diagnostics(),
            "drive_stats": self.drive_system.get_personality_summary(),
            "critic_stats": self.internal_critic.get_stats(),
            "working_set_stats": self.working_set.get_summary(),
            "resilience_stats": self.resilience_manager.get_health_status(),
            "memory_stats": {
                "short_term_count": len(self.short_term_memory.get_all()) if hasattr(self.short_term_memory, 'get_all') else 0,
                "long_term_count": self.memory_graph.get_stats().get("total_nodes", 0) if hasattr(self.memory_graph, 'get_stats') else 0,
                "graph_stats": self.memory_graph.get_stats() if hasattr(self.memory_graph, 'get_stats') else {}
            }
        }
