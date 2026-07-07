"""
Main Loop - Loop principal do agente autônomo

Integra todos os componentes:
- Estado
- Cognição (intenção, pensamento, planejamento)
- Gatilhos
- Modos
- Prioridades
- Reflexão
- Alinhamento Ético (Alignment Engine)
- Crítico Interno (InternalCritic)
- Interpretação Contínua (ContinuousInterpreter)
- Memória de Trabalho (WorkingMemorySet)
- Resiliência (ResilienceModule)
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
from agent.core.cognition.boredom import BoredomEngine, BoredomLevel, BoredomAction
from agent.core.cognition.drive import DriveSystem, DriveType, MotivationalState
from agent.core.cognition.critic import InternalCritic, CritiqueReport, CriticSeverity
from agent.core.cognition.interpretation import ContinuousInterpreter, RawInput, InterpretationLayer
from agent.core.cognition.working_set import WorkingMemorySet
from agent.core.autonomy.mode_manager import ModeManager, Mode
from agent.core.autonomy.priorities import PriorityManager
from agent.core.autonomy.triggers import TriggerManager
from agent.core.autonomy.resilience import ResilienceManager, ErrorContext, ErrorSeverity, safe_execute

# Importa Alignment Engine para verificação ética
from agent.safety.alignment import AlignmentEngine, AlignmentConfig


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
        
        # Inicializa sistemas de motivação interna (Boredom e Drives)
        personality_profile = self.config.get("personality_profile", "balanced")
        self.boredom_engine = BoredomEngine()
        self.drive_system = DriveSystem(personality_profile=personality_profile)
        
        # Inicializa módulos cognitivos adicionais
        self.critic = InternalCritic()
        self.interpreter = ContinuousInterpreter()
        self.working_set = WorkingMemorySet(
            max_items=self.config.get("max_working_items", 20),
            ttl_seconds=self.config.get("working_set_ttl", 600)
        )
        
        # Inicializa sistema de resiliência
        self.resilience = ResilienceManager()
        
        self.mode_manager = ModeManager(
            initial_mode=Mode[self.config.get("initial_mode", "WORK").upper()]
        )
        self.priority_manager = PriorityManager()
        self.trigger_manager = TriggerManager()
        
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
        
        # Atualiza sistemas de motivação interna (Boredom e Drives)
        is_executing = status.state == AgentState.EXECUTING
        has_user_tasks = self.priority_manager.has_user_tasks()
        
        # Update Boredom Engine
        boredom_state = self.boredom_engine.update(
            has_user_tasks=has_user_tasks,
            is_executing=is_executing,
            recent_discoveries=0  # Pode ser incrementado com descobertas reais
        )
        
        # Update Drive System
        motivational_state = self.drive_system.update(
            recent_actions=[],
            environment_changes=0,
            user_interactions=1 if has_user_tasks else 0,
            completed_tasks=0
        )
        
        # Obtém status de resiliência
        resilience_status = self.resilience.get_health_status()
        
        return {
            "state": status.state,
            "mode": status.mode,
            "idle_time": idle_time,
            "has_user_tasks": has_user_tasks,
            "cycle_count": self.cycle_count,
            "errors_in_cycle": status.errors_in_cycle,
            "llm_calls_in_cycle": status.llm_calls_in_cycle,
            "context_summary": self.context_manager.get_summary(),
            # Estados motivacionais internos
            "boredom_level": boredom_state.level,
            "boredom_score": boredom_state.score,
            "motivational_state": motivational_state,
            # Status de resiliência
            "resilience_status": resilience_status,
            # Working set summary
            "working_set_summary": self.working_set.get_summary()
        }
    
    def _check_triggers(self) -> list:
        """Fase 2-4: Verificar gatilhos"""
        active_triggers = self.trigger_manager.get_active_triggers()
        
        for trigger in active_triggers:
            self.logger.debug(f"Gatilho ativo: {trigger.id} ({trigger.description})")
            self.trigger_manager.fire_trigger(trigger.id)
        
        return active_triggers
    
    def _determine_intention(self, observation: Dict) -> IntentionType:
        """Fase 5: Definir intenção - agora influenciada por tédio e drives internos"""
        mode_value = observation["mode"].value if hasattr(observation["mode"], 'value') else observation["mode"]
        
        # Obtém estados motivacionais
        boredom_level = observation.get("boredom_level")
        boredom_score = observation.get("boredom_score", 0.0)
        motivational_state = observation.get("motivational_state")
        
        # Verifica se sistemas de motivação sugerem ação autônoma
        suggested_boredom_action = self.boredom_engine.get_suggested_action()
        drive_suggestions = self.drive_system.get_action_suggestions()
        
        # Se tédio alto e sem tarefas do usuário, considera ação autônoma
        if not observation["has_user_tasks"] and boredom_score > 60:
            # Tédio significativo pode gerar intenção de explorar ou aprender
            if suggested_boredom_action == BoredomAction.EXPLORE:
                self.logger.info(f"🎯 Tédio alto ({boredom_score:.1f}) sugere EXPLORAR")
                # Registra no contexto
                self.context_manager.add_thought(
                    f"[MOTIVAÇÃO INTERNA] Tédio: {boredom_score:.1f} - Sugerindo exploração autônoma"
                )
            elif suggested_boredom_action == BoredomAction.LEARN:
                self.logger.info(f"📚 Tédio alto ({boredom_score:.1f}) sugere APRENDER")
                self.context_manager.add_thought(
                    f"[MOTIVAÇÃO INTERNA] Tédio: {boredom_score:.1f} - Sugerindo aprendizado"
                )
            elif suggested_boredom_action == BoredomAction.ASK_USER:
                # Gera mensagem de tédio
                boredom_msg = self.boredom_engine.generate_boredom_message()
                self.logger.info(f"💬 {boredom_msg}")
                self.context_manager.add_thought(f"[MOTIVAÇÃO INTERNA] {boredom_msg}")
        
        # Drives dominantes podem influenciar intenção
        if motivational_state and motivational_state.dominant_drive:
            dominant = motivational_state.dominant_drive
            tension = motivational_state.overall_tension
            
            if tension > 40 and not observation["has_user_tasks"]:
                self.logger.debug(f"🔥 Drive dominante: {dominant.value} (tensão: {tension:.1f})")
                self.context_manager.add_thought(
                    f"[DRIVE INTERNO] {dominant.value} com tensão {tension:.1f}"
                )
        
        # Avalia intenção normal (pode ser sobreescrita por motivação interna)
        intention = self.intention_engine.evaluate(
            has_user_tasks=observation["has_user_tasks"],
            idle_time=observation["idle_time"],
            mode=mode_value,
            context_summary=observation.get("context_summary"),
            errors_recent=observation["errors_in_cycle"],
            llm_calls_recent=observation["llm_calls_in_cycle"],
            max_llm_calls=self.config.get("max_llm_calls_per_cycle", 3)
        )
        
        # Se intenção for NO_ACT/WAIT mas há motivação interna forte, muda para EXPLORE/LEARN
        if intention.intention_type in [IntentionType.NO_ACT, IntentionType.WAIT]:
            if boredom_score > 70 or (motivational_state and motivational_state.overall_tension > 50):
                # Motivação interna forte supera inatividade
                if suggested_boredom_action in [BoredomAction.EXPLORE, BoredomAction.LEARN]:
                    intention.intention_type = IntentionType.EXPLORE
                    intention.reason = f"Motivação interna: {suggested_boredom_action.value} (tédio: {boredom_score:.1f})"
                    self.logger.info(f"🔄 Intenção alterada para EXPLORE por motivação interna")
        
        self.context_manager.set_intention(intention.intention_type.value)
        self.logger.info(f"Intenção determinada: {intention.intention_type.value} - {intention.reason}")
        
        return intention.intention_type
    
    def _interpret_input(self, raw_data: Any, source: str = "environment") -> Dict:
        """Fase intermediária: Interpretar dados brutos antes do pensamento"""
        raw_input = RawInput(
            source=source,
            content_type="text" if isinstance(raw_data, str) else "event",
            raw_data=raw_data,
            context_snapshot={
                "mode": self.mode_manager.get_mode().value,
                "state": self.state_manager.get_status().state.value,
                "has_user_tasks": self.priority_manager.has_user_tasks()
            }
        )
        
        interpretations = self.interpreter.interpret(raw_input)
        
        # Pega a interpretação de maior confiança
        best_interpretation = interpretations[0] if interpretations else None
        
        if best_interpretation:
            # Registra ambiguidades se houver
            if best_interpretation.ambiguities:
                self.logger.warning(f"Ambiguidades detectadas: {best_interpretation.ambiguities}")
            
            # Registra tom emocional
            if best_interpretation.emotional_tone and best_interpretation.emotional_tone != "neutral":
                self.context_manager.add_thought(
                    f"[INTERPRETAÇÃO] Tom emocional: {best_interpretation.emotional_tone}"
                )
        
        return {
            "interpretations": [i.to_dict() for i in interpretations],
            "best_match": best_interpretation.to_dict() if best_interpretation else None,
            "ambiguity_alerts": self.interpreter.get_ambiguity_alerts()
        }
    
    def _think(self, intention: IntentionType) -> Optional[str]:
        """Fase 6: Pensar sobre a ação (interno, não exposto)."""
        if intention == IntentionType.NO_ACT:
            # Mesmo em NO_ACT, pode haver pensamento espontâneo
            thought = self.thinking_engine.spontaneous_thought()
            if thought:
                self.logger.info(f"🧠 Pensamento autônomo gerado: {thought.conclusion}")
                # Registra no contexto interno
                for step in thought.steps:
                    self.context_manager.add_thought(f"[AUTÔNOMO] {step.content}")
            return None
        
        if intention == IntentionType.WAIT:
            # Mesmo em WAIT, pode haver pensamento espontâneo
            thought = self.thinking_engine.spontaneous_thought()
            if thought:
                self.logger.info(f"🧠 Pensamento autônomo gerado: {thought.conclusion}")
                # Registra no contexto interno
                for step in thought.steps:
                    self.context_manager.add_thought(f"[AUTÔNOMO] {step.content}")
            return None
        
        # Inicia processo de pensamento REATIVO
        question = f"Como proceder com intenção: {intention.value}?"
        self.thinking_engine.start_thinking(question)
        
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
        
        # Registra pensamentos no contexto (INTERNO - não exposto ao usuário)
        for step in process.steps:
            self.context_manager.add_thought(step.content)
        
        self.logger.debug(f"Pensamento interno concluído: {process.conclusion}")
        return action
    
    def _plan(self, action: str) -> bool:
        """Fase 7: Planejar ação - agora com validação do crítico interno e working set"""
        if not action:
            return False
        
        # Usa working set para rascunho mental antes do planejamento final
        self.working_set.add_idea(
            content=f"Ação planejada: {action}",
            tags=["planning", "action"],
            confidence=0.7
        )
        
        # Cria plano inicial
        plan = self.planner.create_plan(action)
        
        # Prepara dados para validação do crítico
        plan_data = {
            "id": f"plan_{self.cycle_count}",
            "goal": action,
            "actions": [
                {"id": step.id, "name": step.description, "depends_on": [], "risk_level": "low"}
                for step in plan.steps
            ],
            "required_resources": [],
            "estimated_time_seconds": len(plan.steps) * 30,
            "fallback_plan": None
        }
        
        # Contexto para o crítico
        context = {
            "available_resources": ["file_system", "web_search", "code_analysis"],
            "max_execution_time_seconds": 300,
            "agent_mode": self.mode_manager.get_mode().value
        }
        
        # Valida plano com InternalCritic
        critique_report = self.critic.evaluate_plan(plan_data, context)
        
        # Registra críticas no working set
        for critique in critique_report.critiques:
            self.working_set.add_hypothesis(
                hypothesis=f"Crítica: {critique.issue}",
                related_to=[plan_data["id"]]
            )
            
            if critique.severity in [CriticSeverity.CRITICAL, CriticSeverity.HIGH]:
                self.logger.warning(f"⚠️ Crítico: {critique.issue} - {critique.suggestion}")
                # Adiciona restrição ao working set
                self.working_set.add_constraint(
                    constraint=critique.issue,
                    severity=critique.severity.value
                )
        
        # Se plano não foi aprovado, tenta refinamento
        if not critique_report.is_approved:
            critical_issues = critique_report.get_critical_issues()
            self.logger.warning(f"Plano reprovado pelo crítico: {len(critical_issues)} issues críticos")
            
            # Descarta ideias relacionadas ao plano falho
            for item_id in list(self.working_set.items.keys()):
                if plan_data["id"] in self.working_set.items[item_id].related_items:
                    self.working_set.discard_item(item_id, reason="plan_rejected")
            
            return False
        
        # Plano aprovado - promove itens do working set
        for item in self.working_set.get_active_items():
            if item.confidence >= 0.8:
                self.working_set.promote_item(item.id)
        
        # Exporta working set para contexto de planejamento
        exported = self.working_set.export_for_planning()
        if exported["promoted_items"] or exported["high_confidence_ideas"]:
            self.context_manager.add_thought(
                f"[WORKING SET] {len(exported['promoted_items'])} itens promovidos, "
                f"{len(exported['high_confidence_ideas'])} ideias de alta confiança"
            )
        
        self.context_manager.set_plan([step.description for step in plan.steps])
        
        self.logger.info(f"Plano criado e validado: {action} ({len(plan.steps)} etapas)")
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
                
                # REGISTRA ESTIMULAÇÃO nos sistemas de motivação (reduz tédio e satisfaz drives)
                action_description = result.description.lower()
                
                # Registra no Boredom Engine
                boredom_impact = 15.0  # Redução padrão do tédio
                if "explor" in action_description:
                    boredom_impact = 20.0
                elif "aprend" in action_description or "estud" in action_description:
                    boredom_impact = 18.0
                
                self.boredom_engine.record_stimulation(
                    event_type="self_initiated" if plan.intention == "Explorar contexto em busca de aprendizado" else "task_completion",
                    description=result.description,
                    impact=boredom_impact
                )
                
                # Satisfaz drives relevantes no Drive System
                if "organiz" in action_description:
                    self.drive_system.satisfy_drive(DriveType.ORDER, 15.0)
                if "otimiz" in action_description:
                    self.drive_system.satisfy_drive(DriveType.EFFICIENCY, 15.0)
                if "explor" in action_description:
                    self.drive_system.satisfy_drive(DriveType.CURIOSITY, 18.0)
                if "aprend" in action_description or "estud" in action_description:
                    self.drive_system.satisfy_drive(DriveType.LEARNING, 18.0)
                if "tarefa" in action_description or "conclu" in action_description:
                    self.drive_system.satisfy_drive(DriveType.COMPLETION, 20.0)
                    self.drive_system.satisfy_drive(DriveType.PURPOSE, 15.0)
                
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
            # Usa ResilienceManager para tratar erro
            error_ctx = ErrorContext(
                error_type=type(e).__name__,
                message=str(e),
                module="agent_loop",
                function="_execute",
                severity=self.resilience.classify_error(e),
                original_exception=e,
                context_data={"step_id": step.id if step else None}
            )
            
            # Trata erro com resiliência
            recovered = self.resilience.handle_error(error_ctx)
            
            self.planner.fail_step(step.id, str(e))
            self.state_manager.increment_error()
            self.logger.error(f"Erro na execução: {e}")
            
            # Se não recuperado, limpa working set
            if not recovered:
                self.working_set.reset()
            
            return False
    
    def _reflect(self):
        """Fase 9: Refletir sobre ações - agora inclui limpeza do working set e atualização de resiliência"""
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
        
        # Registra lições aprendidas no working set antes de limpar
        for lesson in reflection.lessons_learned:
            self.working_set.add_idea(
                content=f"Lição: {lesson}",
                tags=["lesson_learned", "reflection"],
                confidence=0.9
            )
        
        # Limpa working set após ciclo completo (fim do ciclo cognitivo)
        self.working_set.clear_discarded()
        
        # Reseta saúde da resiliência após sucesso
        self.resilience.reset_health()
        
        self.logger.info(f"Reflexão criada: {len(reflection.lessons_learned)} lições aprendidas")
    
    def _register(self):
        """Fase 10: Registrar ciclo - agora inclui estatísticas dos módulos integrados"""
        self.cycle_count += 1
        self.state_manager.increment_cycle()
        self.state_manager.update_last_action()
        
        # Limpa interpretações antigas periodicamente
        if self.cycle_count % 50 == 0:
            self.interpreter.clear_history()
    
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
        """Retorna status completo do agente incluindo todos os módulos cognitivos"""
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
            # Estatísticas dos módulos cognitivos integrados
            "boredom_stats": {
                "current_level": self.boredom_engine._current_level.value if hasattr(self.boredom_engine, '_current_level') else None,
                "current_score": self.boredom_engine._current_score if hasattr(self.boredom_engine, '_current_score') else None
            },
            "drive_stats": self.drive_system.get_profile() if hasattr(self.drive_system, 'get_profile') else {},
            "critic_stats": self.critic.get_stats() if hasattr(self.critic, 'get_stats') else {},
            "working_set_stats": self.working_set.get_summary(),
            "interpreter_stats": {
                "history_size": len(self.interpreter.interpretation_history),
                "context_memory_size": len(self.interpreter.context_memory)
            },
            "resilience_stats": self.resilience.get_health_status()
        }
