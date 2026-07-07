"""
Main Loop - Loop principal do agente autônomo

Integra todos os componentes:
- Estado
- Cognição (intenção, pensamento, planejamento)
- Gatilhos
- Modos
- Prioridades
- Reflexão
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
from agent.core.autonomy.mode_manager import ModeManager, Mode
from agent.core.autonomy.priorities import PriorityManager
from agent.core.autonomy.triggers import TriggerManager


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
    7. Executar (quando implementado)
    8. Registrar
    9. Refletir
    10. Aguardar próximo ciclo
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
        
        return {
            "state": status.state,
            "mode": status.mode,
            "idle_time": idle_time,
            "has_user_tasks": self.priority_manager.has_user_tasks(),
            "cycle_count": self.cycle_count,
            "errors_in_cycle": status.errors_in_cycle,
            "llm_calls_in_cycle": status.llm_calls_in_cycle,
            "context_summary": self.context_manager.get_summary()
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
        """Fase 7: Planejar ação"""
        if not action:
            return False
        
        plan = self.planner.create_plan(action)
        self.context_manager.set_plan([step.description for step in plan.steps])
        
        self.logger.info(f"Plano criado: {action} ({len(plan.steps)} etapas)")
        return True
    
    def _execute(self) -> bool:
        """Fase 8: Executar ação e gerar resposta ao usuário usando executor real"""
        plan = self.planner.get_current_plan()
        if not plan:
            return False
        
        step = self.planner.get_next_step()
        if not step:
            return True  # Plano completo
        
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
                    "plan_intention": plan.intention
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
    
    def _register(self):
        """Fase 10: Registrar ciclo"""
        self.cycle_count += 1
        self.state_manager.increment_cycle()
        self.state_manager.update_last_action()
    
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
            }
        }
