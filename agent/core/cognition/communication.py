"""
Módulo de Comunicação e Resposta ao Usuário.
Responsável por transformar pensamentos internos em respostas conversacionais.
Aqui ocorre a tradução da intenção cognitiva para linguagem natural.
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import json

@dataclass
class UserResponse:
    """
    Estrutura da resposta enviada ao usuário.
    Diferente do ThoughtProcess, isso É visível.
    """
    timestamp: datetime = field(default_factory=datetime.now)
    content: str = ""
    tone: str = "neutral"  # neutral, friendly, professional, urgent
    source: str = "internal"  # internal, llm, tool_result
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "timestamp": self.timestamp.isoformat(),
            "content": self.content,
            "tone": self.tone,
            "source": self.source,
            "metadata": self.metadata
        }


class CommunicationEngine:
    """
    Motor de Comunicação.
    
    Responsabilidades:
    1. Receber conclusão do ThinkingEngine
    2. Decidir SE comunicar (alguns pensamentos não geram fala)
    3. Formatrar resposta em linguagem natural
    4. Manter histórico de conversas
    5. Adaptar tom baseado no contexto
    
    Separação crítica:
    - ThinkingEngine: "O que eu acho que devo fazer"
    - CommunicationEngine: "Como eu digo isso ao usuário"
    """
    
    def __init__(self):
        self.conversation_history: List[Dict[str, Any]] = []
        self.current_response: Optional[UserResponse] = None
        self.suppress_mode = False  # Se True, não gera saída verbal
        
    def generate_response(
        self, 
        thought_conclusion: str,
        action_taken: Optional[str] = None,
        context: Dict[str, Any] = None
    ) -> UserResponse:
        """
        Gera resposta baseada na conclusão do pensamento.
        
        Args:
            thought_conclusion: Conclusão do ThinkingEngine
            action_taken: Ação que foi/will ser executada
            context: Contexto adicional (modo, estado, etc.)
            
        Returns:
            UserResponse pronta para ser exibida
        """
        context = context or {}
        mode = context.get('mode', 'work')
        state = context.get('state', 'idle')
        
        # Decide se deve falar
        if self._should_remain_silent(thought_conclusion, mode):
            self.suppress_mode = True
            return UserResponse(
                content="",
                tone="silent",
                metadata={"reason": "silent_by_design"}
            )
        
        # Constrói resposta baseada no tipo de conclusão
        response_content = self._craft_response(
            thought_conclusion, 
            action_taken,
            mode
        )
        
        # Determina tom
        tone = self._determine_tone(thought_conclusion, state)
        
        self.current_response = UserResponse(
            content=response_content,
            tone=tone,
            source="internal",
            metadata={
                "thought_conclusion": thought_conclusion,
                "action_taken": action_taken,
                "mode": mode
            }
        )
        
        # Adiciona ao histórico
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "role": "assistant",
            "content": response_content,
            "tone": tone
        })
        
        return self.current_response
    
    def _should_remain_silent(self, conclusion: str, mode: str) -> bool:
        """
        Decide se o agente deve permanecer em silêncio.
        
        Regras:
        - Em modo 'work', pensamentos muito internos não são verbalizados
        - Reflexões pós-ação podem ser silenciosas
        - Pensamentos de baixa confiança (<0.3) não são compartilhados
        """
        silent_keywords = ["internal", "self-check", "validation", "preparation"]
        
        if mode == "work":
            # Em modo trabalho, só fala se for relevante para o usuário
            if any(kw in conclusion.lower() for kw in silent_keywords):
                return True
                
        return False
    
    def _craft_response(
        self, 
        conclusion: str, 
        action: Optional[str],
        mode: str
    ) -> str:
        """
        Constrói a resposta em linguagem natural usando LLM REAL.
        
        Estrutura típica:
        1. Reconhecimento (se aplicável)
        2. Explicação breve do raciocínio (opcional)
        3. Ação tomada ou recomendada
        4. Próximo passo (opcional)
        """
        from agent.infra.llm.client import LLMMessage
        from agent.infra.llm.router import LLMRouter
        
        # Tenta usar LLM real para gerar resposta natural
        router = LLMRouter()
        
        system_prompt = f"""Você é a interface de comunicação de um agente autônomo.
Sua tarefa é transformar conclusões técnicas em respostas naturais e conversacionais em português.
Modo atual: {mode}
- Se 'work': seja direto, profissional e focado na ação
- Se 'free': seja mais explicativo e amigável

Não mencione processos internos, pensamentos ou steps. Apenas responda naturalmente."""

        user_prompt = f"""Conclusão interna: {conclusion}
Ação executada: {action if action else 'Nenhuma'}

Gere uma resposta natural e concisa para o usuário."""
        
        try:
            messages = [
                LLMMessage(role="system", content=system_prompt),
                LLMMessage(role="user", content=user_prompt)
            ]
            
            # Tenta usar LLM real (método correto: chat_completion)
            router = LLMRouter()
            response = router.chat_completion(
                messages=messages,
                purpose="resposta_usuario"
            )
            
            if response and not response.error and response.content.strip():
                return response.content.strip()
                
        except Exception as e:
            print(f"[WARNING] LLM indisponível para comunicação, usando fallback: {e}")
        
        # FALLBACK: Respostas pré-moldadas se LLM não estiver disponível
        parts = []
        
        # Se há ação, menciona primeiro
        if action:
            parts.append(f"Ação executada: {action}")
        
        # Adiciona conclusão de forma adaptativa
        if mode == "free":
            # Em modo livre, é mais explicativo
            parts.append(f"Estou analisando: {conclusion}")
        else:
            # Em modo trabalho, é mais direto
            parts.append(conclusion)
        
        return "\n".join(parts) if parts else "Entendido."
    
    def _determine_tone(self, conclusion: str, state: str) -> str:
        """Determina o tom da resposta baseado no conteúdo e estado."""
        urgent_keywords = ["crítico", "erro", "falha", "urgente", "perigo"]
        
        if any(kw in conclusion.lower() for kw in urgent_keywords):
            return "urgent"
        
        if state == "exploring":
            return "friendly"
        
        if state == "executing":
            return "professional"
        
        return "neutral"
    
    def add_user_message(self, content: str, metadata: Dict = None):
        """Registra mensagem do usuário no histórico."""
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "role": "user",
            "content": content,
            "metadata": metadata or {}
        })
    
    def get_conversation_summary(self, last_n: int = 10) -> List[Dict]:
        """Retorna resumo das últimas trocas de mensagens."""
        return self.conversation_history[-last_n:]
    
    def clear_history(self):
        """Limpa histórico de conversas."""
        self.conversation_history.clear()
    
    def export_conversation(self, filepath: str):
        """Exporta conversa completa para arquivo JSON."""
        with open(filepath, 'w') as f:
            json.dump(self.conversation_history, f, indent=2, ensure_ascii=False)
    
    def get_last_response(self) -> Optional[UserResponse]:
        """Retorna última resposta gerada."""
        return self.current_response


# Exemplo de uso integrado
class CognitiveLoop:
    """
    Exemplo de como Thinking e Communication trabalham juntos.
    Isso será integrado no main_loop.py
    """
    
    def __init__(self):
        from .thinking import ThinkingEngine
        self.thinking = ThinkingEngine(max_depth=3)
        self.communication = CommunicationEngine()
    
    def process_input(self, user_input: str, context: Dict = None):
        """
        Fluxo completo:
        1. Usuário fala
        2. Agente pensa (interno)
        3. Agente decide se responde
        4. Agente responde (externo)
        """
        context = context or {}
        
        # Passo 1: Pensamento interno (NÃO visível)
        thought_process = self.thinking.start_thinking(user_input, context)
        self.thinking.add_thought_step("Analisando intenção do usuário...")
        self.thinking.add_thought_step("Verificando restrições de segurança...")
        
        conclusion = "Devo executar a tarefa solicitada com cautela."
        self.thinking.conclude(conclusion=conclusion, action="execute_task")
        
        # Passo 2: Geração de resposta (visível)
        response = self.communication.generate_response(
            thought_conclusion=conclusion,
            action_taken="execute_task",
            context=context
        )
        
        # Passo 3: Retorna apenas a resposta (pensamento fica logado internamente)
        return response


if __name__ == "__main__":
    # Teste rápido
    loop = CognitiveLoop()
    result = loop.process_input(
        "Liste os arquivos do diretório atual",
        context={"mode": "work", "state": "idle"}
    )
    
    print("=" * 60)
    print("PENSAMENTO INTERNO (Logs internos - não mostrado ao usuário):")
    print("=" * 60)
    for step in loop.thinking.history[-1].steps:
        print(f"  [Passo {step.step_number}] {step.content}")
    
    print("\n" + "=" * 60)
    print("RESPOSTA AO USUÁRIO (O que é dito):")
    print("=" * 60)
    print(f"Tom: {result.tone}")
    print(f"Conteúdo:\n{result.content}")
