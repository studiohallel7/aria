"""
Thinking Engine - Motor de pensamento interno do agente

Separa pensamento interno de ação e comunicação
"""

from typing import List, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json
import random


@dataclass
class ThoughtStep:
    """Passo individual no processo de pensamento"""
    step_number: int
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    confidence: float = 0.0  # 0-1, confiança neste passo
    
    def to_dict(self) -> Dict:
        return {
            "step_number": self.step_number,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "confidence": self.confidence
        }


@dataclass
class ThinkingProcess:
    """Processo completo de pensamento"""
    id: str
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    steps: List[ThoughtStep] = field(default_factory=list)
    conclusion: Optional[str] = None
    action_recommended: Optional[str] = None
    confidence_final: float = 0.0
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "steps": [s.to_dict() for s in self.steps],
            "conclusion": self.conclusion,
            "action_recommended": self.action_recommended,
            "confidence_final": self.confidence_final
        }


class ThinkingEngine:
    """
    Motor de Pensamento Autônomo.
    
    Diferenciação Crítica:
    - Este motor NÃO depende exclusivamente de input do usuário.
    - Ele pode gerar pensamentos espontâneos baseados em curiosidade, 
      padrões detectados ou necessidade de consolidação de memória.
    - Separação estrita: O processo de pensamento é interno; apenas 
      a conclusão (se relevante) é comunicada.
    """
    
    def __init__(self, max_depth: int = 5, max_time: int = 30):
        self.max_depth = max_depth
        self.max_time = max_time  # segundos
        self.current_process: Optional[ThinkingProcess] = None
        self.history: List[ThinkingProcess] = []
        self.context_data: Dict = {}  # Dados do contexto para pensamento autônomo
    
    def set_context(self, context: Dict):
        """Atualiza contexto interno para pensamento autônomo."""
        self.context_data = context
    
    def start_thinking(self, question: str, context: Dict = None) -> ThinkingProcess:
        """Inicia processo de pensamento REATIVO (estimulado externamente)."""
        if context:
            self.context_data.update(context)
        return self._run_thinking_cycle(question, trigger_type="reactive", source="user")

    def spontaneous_thought(self) -> Optional[ThinkingProcess]:
        """
        PENSAMENTO AUTÔNOMO (O Coração da Autonomia).
        
        Este método é chamado pelo loop principal quando não há input do usuário.
        Ele varre o estado interno, memória recente e contexto para gerar
        insights próprios.
        
        Gatilhos internos:
        1. Curiosidade (aleatoriedade ponderada pelo contexto)
        2. Consolidação (memória de curto prazo precisa ser arquivada)
        3. Padrões (detecção de anomalias ou repetições no ambiente)
        4. Manutenção (verificação de integridade do sistema)
        """
        import random
        
        # Verifica se há contexto suficiente para pensar
        if not self.context_data and not self.history:
            return None
            
        # Gerador de tópicos internos
        topics = self._generate_internal_topics()
        
        if not topics:
            return None
            
        selected_topic = random.choice(topics)
        
        print(f"[AUTONOMY] 🧠 Pensamento espontâneo iniciado sobre: {selected_topic['topic']}")
        return self._run_thinking_cycle(
            content=selected_topic['prompt'], 
            trigger_type="spontaneous",
            source="internal"
        )

    def _generate_internal_topics(self) -> List[Dict[str, str]]:
        """Gera tópicos baseados no estado atual e memória."""
        topics = []
        
        # 1. Consolidação de Memória (baseado no histórico de pensamentos)
        if len(self.history) > 5:
            topics.append({
                "topic": "Memory Consolidation",
                "prompt": "Analise os últimos processos de pensamento. Existem padrões recorrentes? Alguma conclusão deve ser reforçada ou revisada?"
            })
            
        # 2. Verificação de Estado (Self-Health)
        if random.random() < 0.3: # 30% de chance se ocioso
            topics.append({
                "topic": "System Health",
                "prompt": "Revise o estado atual do sistema. Os recursos estão sendo utilizados de forma eficiente? Há alguma otimização possível?"
            })
            
        # 3. Curiosidade Baseada em Contexto
        if self.context_data.get("last_file_change"):
            topics.append({
                "topic": "Context Curiosity",
                "prompt": f"O arquivo {self.context_data['last_file_change']} foi modificado. Isso impacta alguma tarefa pendente ou conhecimento armazenado?"
            })
            
        # 4. Aprendizado Contínuo
        if self.context_data.get("recent_errors"):
            topics.append({
                "topic": "Learning from Errors",
                "prompt": f"Foram detectados {len(self.context_data['recent_errors'])} erros recentes. O que podemos aprender para evitar repetição?"
            })
            
        return topics

    def _run_thinking_cycle(self, content: str, trigger_type: str, source: str) -> ThinkingProcess:
        """Executa ciclo completo de pensamento usando LLM REAL."""
        from agent.infra.llm.client import get_client, LLMMessage
        from agent.infra.llm.router import LLMRouter
        
        process_id = f"think_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{trigger_type}"
        
        process = ThinkingProcess(
            id=process_id,
            steps=[ThoughtStep(
                step_number=0,
                content=f"[{trigger_type.upper()}] Estímulo: {content}",
                confidence=1.0
            )]
        )
        
        self.current_process = process
        
        # Tenta usar LLM real para gerar cadeia de pensamento
        client = get_client()
        router = LLMRouter()
        
        # Monta prompt para pensamento Chain-of-Thought
        system_prompt = """Você é o motor de pensamento interno de um agente autônomo.
Sua tarefa é analisar profundamente o estímulo recebido e gerar passos de raciocínio lógicos.
Responda APENAS com uma lista numerada de 3 a 5 passos de pensamento, seguidos de uma conclusão.
Formato:
1. [Passo 1]
2. [Passo 2]
...
Conclusão: [Sua conclusão]"""

        user_prompt = f"Estímulo ({trigger_type} de {source}): {content}\n\nContexto atual: {json.dumps(self.context_data, default=str)[:500]}"
        
        try:
            # Seleciona modelo rápido para pensamento interno
            messages = [
                LLMMessage(role="system", content=system_prompt),
                LLMMessage(role="user", content=user_prompt)
            ]
            
            # Tenta chamar LLM real (método correto: chat_completion)
            router = LLMRouter()
            response = router.chat_completion(
                messages=messages,
                purpose="raciocinio_rapido"
            )
            
            if response and not response.error and response.content.strip():
                # Parse da resposta do LLM para extrair passos
                lines = response.content.strip().split('\n')
                thought_steps = []
                conclusion_text = None
                
                for line in lines:
                    line = line.strip()
                    if line.lower().startswith("conclusão:") or line.lower().startswith("conclusion:"):
                        conclusion_text = line.split(":", 1)[1].strip()
                    elif line[0].isdigit() and "." in line:
                        thought_content = line.split(".", 1)[1].strip()
                        thought_steps.append(thought_content)
                
                # Adiciona passos gerados pelo LLM
                for i, step_content in enumerate(thought_steps[:self.max_depth], start=1):
                    step = ThoughtStep(
                        step_number=i,
                        content=step_content,
                        confidence=0.9 - (i * 0.1)
                    )
                    process.steps.append(step)
                
                # Usa conclusão do LLM ou gera uma padrão
                if not conclusion_text:
                    conclusion_text = f"Análise concluída após {len(thought_steps)} passos de raciocínio."
                
                # Decide ação baseada no conteúdo
                action = self._infer_action_from_conclusion(conclusion_text, trigger_type)
                
                self.conclude(conclusion_text, action, confidence=0.85)
                return process
                
        except Exception as e:
            print(f"[WARNING] LLM indisponível, usando pensamento simulado: {e}")
        
        # FALLBACK: Simulação se LLM não estiver disponível (sem API key, etc)
        print(f"[MOCK MODE] Gerando pensamentos simulados...")
        current_thought = content
        for i in range(1, min(self.max_depth, random.randint(2, 4))):
            step_content = f"Analisando implicações de: {current_thought[:60]}..."
            step = ThoughtStep(
                step_number=i,
                content=step_content,
                confidence=0.9 - (i * 0.1)
            )
            process.steps.append(step)
            current_thought = step_content
            
        conclusion = f"Conclusão gerada após análise de {len(process.steps)} passos."
        action = None
        
        if trigger_type == "spontaneous" and random.random() > 0.7:
            action = "monitor_resources"
        elif trigger_type == "reactive":
            action = "respond_to_user"
            
        self.conclude(conclusion, action, confidence=0.85)
        
        return process
    
    def _infer_action_from_conclusion(self, conclusion: str, trigger_type: str) -> Optional[str]:
        """Infere ação recomendada baseada na conclusão."""
        conclusion_lower = conclusion.lower()
        
        if any(word in conclusion_lower for word in ["erro", "problema", "falha", "ajustar"]):
            return "fix_issue"
        elif any(word in conclusion_lower for word in ["arquivo", "salvar", "criar", "modificar"]):
            return "file_operation"
        elif any(word in conclusion_lower for word in ["perguntar", "usuário", "responder"]):
            return "respond_to_user"
        elif any(word in conclusion_lower for word in ["otimizar", "melhorar", "eficiente"]):
            return "optimize_system"
        elif trigger_type == "spontaneous":
            return "log_insight"
        
        return None
    
    def add_thought_step(self, content: str, confidence: float = 0.5) -> Optional[ThoughtStep]:
        """
        Adiciona passo ao pensamento atual
        
        Returns None se profundidade máxima atingida
        """
        if self.current_process is None:
            return None
        
        if len(self.current_process.steps) >= self.max_depth:
            return None
        
        step = ThoughtStep(
            step_number=len(self.current_process.steps),
            content=content,
            confidence=confidence
        )
        
        self.current_process.steps.append(step)
        return step
    
    def conclude(
        self, 
        conclusion: str, 
        action: Optional[str] = None,
        confidence: float = 0.5
    ) -> ThinkingProcess:
        """Conclui processo de pensamento"""
        if self.current_process is None:
            raise ValueError("Nenhum processo de pensamento ativo")
        
        self.current_process.completed_at = datetime.now()
        self.current_process.conclusion = conclusion
        self.current_process.action_recommended = action
        self.current_process.confidence_final = confidence
        
        # Move para histórico
        finished = self.current_process
        self.history.append(finished)
        self.current_process = None
        
        return finished
    
    def get_current_thoughts(self) -> List[str]:
        """Retorna pensamentos do processo atual"""
        if self.current_process is None:
            return []
        
        return [step.content for step in self.current_process.steps]
    
    def get_last_conclusion(self) -> Optional[str]:
        """Retorna conclusão do último processo"""
        if not self.history:
            return None
        return self.history[-1].conclusion
    
    def get_recent_processes(self, n: int = 5) -> List[ThinkingProcess]:
        """Retorna últimos n processos de pensamento"""
        return self.history[-n:]
    
    def abort_current(self):
        """Aborta processo de pensamento atual"""
        self.current_process = None
    
    def export_process(self, process_id: str, filepath: str):
        """Exporta processo para arquivo"""
        for proc in self.history:
            if proc.id == process_id:
                with open(filepath, 'w') as f:
                    json.dump(proc.to_dict(), f, indent=2)
                return True
        return False
    
    def get_summary(self) -> Dict:
        """Retorna resumo da atividade de pensamento"""
        total_steps = sum(len(p.steps) for p in self.history)
        avg_confidence = (
            sum(p.confidence_final for p in self.history) / len(self.history)
            if self.history else 0.0
        )
        
        # Conta processos por tipo
        reactive_count = sum(1 for p in self.history if "reactive" in p.id)
        spontaneous_count = sum(1 for p in self.history if "spontaneous" in p.id)
        
        return {
            "total_processes": len(self.history),
            "reactive_processes": reactive_count,
            "spontaneous_processes": spontaneous_count,
            "total_steps": total_steps,
            "average_confidence": avg_confidence,
            "max_depth_used": max(len(p.steps) for p in self.history) if self.history else 0,
            "current_active": self.current_process is not None
        }
