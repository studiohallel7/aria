"""
Agente Autônomo com Interface de Voz (Fase 7)
Conecta o cérebro do agente (core, memória, ética) com a interface de voz.
Permite interação natural por voz e execução autônoma.

Requisitos:
    pip install vosk sounddevice edge-tts pygame
    Baixe o modelo Vosk: https://alphacephei.com/vosk/models/vosk-model-small-pt-0.3.zip
"""
import asyncio
import time
import sys
from typing import Optional
from agent.core.main_loop import AgentLoop
from agent.interface.voice import VoiceInterface
from agent.memory.manager import HolographicMemoryGraph
from agent.safety.alignment import AlignmentEngine

class VocalAutonomousAgent:
    """
    Agente que pensa autonomamente mas interage via voz.
    - Escuta comandos do usuário
    - Processa internamente (pensamentos espontâneos)
    - Responde por voz
    - Executa ações reais se configurado
    """
    
    def __init__(self, voice_name: str = "pt-BR-FranciscaNeural"):
        print("🧠 Inicializando Agente Vocal Autônomo...")
        
        # Componentes Cognitivos
        self.memory = HolographicMemoryGraph()
        self.ethics = AlignmentEngine()
        self.brain = AgentLoop()
        
        # Interface de Voz
        self.voice = VoiceInterface(voice_name)
        self.voice.on_speech_detected = self._on_user_speech
        self.voice.on_error = self._on_voice_error
        
        # Estado
        self.is_running = False
        self.last_interaction = time.time()
        
        print("✅ Agente pronto. Diga 'olá' para começar.")

    def _on_user_speech(self, text: str):
        """Callback quando o usuário fala algo."""
        print(f"\n💬 Usuário: {text}")
        self.last_interaction = time.time()
        
        # Processa entrada do usuário
        response = self._process_input(text, source="user")
        
        # Responde por voz
        if response:
            print(f"🤖 Agente: {response}")
            self.voice.speak(response)
            
        # Reativa escuta
        self.voice.start_listening(self._on_user_speech)

    def _on_voice_error(self, error: str):
        """Callback de erros de voz."""
        print(f"❌ Erro de voz: {error}")

    def _process_input(self, text: str, source: str = "user") -> Optional[str]:
        """
        Processa entrada (voz ou pensamento interno) através do ciclo cognitivo.
        1. Verifica ética
        2. Atualiza memória
        3. Gera resposta/pensamento
        """
        # 1. Verificação Ética
        ethical_check = self.ethics.check_action(
            action_description=f"Processar entrada: {text[:50]}...",
            potential_harms=[],
            potential_benefits=["resposta útil", "aprendizado"],
            urgency=0.5
        )
        
        if not ethical_check.approved:
            return f"Desculpe, não posso processar isso devido aos meus princípios: {ethical_check.reasoning}"
        
        # 2. Salvar na Memória
        memory_type = "episodic" if source == "user" else "internal"
        self.memory.add_memory(
            content=text,
            memory_type=memory_type,
            tags=[source, "conversation"],
            importance=0.8 if source == "user" else 0.4
        )
        
        # 3. Processar no Loop Cognitivo (simplificado para demo)
        # Em produção, chamaria self.brain.run_cycle() completo
        response = self._generate_response(text, source)
        
        return response

    def _generate_response(self, input_text: str, source: str) -> str:
        """
        Gera resposta baseada no estado atual.
        NOTA: Aqui entraria a chamada real ao LLM quando configurado.
        """
        # Simulação de resposta inteligente (substituir por LLM real)
        if "olá" in input_text.lower() or "oi" in input_text.lower():
            return "Olá! Estou aqui e pronto para ajudar. O que você gostaria de fazer?"
        
        if "como você está" in input_text.lower():
            drives = self.brain.state.drives if hasattr(self.brain, 'state') else {}
            return "Estou funcionando bem! Meus sistemas estão operacionais."
        
        if "ajuda" in input_text.lower():
            return "Posso ajudar com tarefas, responder perguntas ou apenas conversar. O que precisa?"
        
        # Resposta genérica baseada em contexto
        return f"Entendi: '{input_text}'. Estou processando essa informação e aprendendo com ela."

    def start_autonomous_mode(self):
        """Inicia modo autônomo: pensa sozinho quando ocioso."""
        print("\n🚀 Iniciando modo autônomo...")
        self.is_running = True
        self.voice.start_listening(self._on_user_speech)
        
        try:
            while self.is_running:
                idle_time = time.time() - self.last_interaction
                
                # Se ocioso por > 10 segundos, gera pensamento espontâneo
                if idle_time > 10 and idle_time % 15 < 1:  # A cada ~15s
                    thought = self._generate_spontaneous_thought()
                    if thought:
                        print(f"\n💭 [Pensamento Espontâneo]: {thought}")
                        # Opcional: falar o pensamento em voz alta
                        # self.voice.speak(thought)
                        
                        # Processa internamente
                        self._process_input(thought, source="internal")
                
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n⏹️  Parando agente...")
            self.stop()

    def _generate_spontaneous_thought(self) -> Optional[str]:
        """Gera um pensamento espontâneo baseado no estado atual."""
        # Em produção, usaria o IntrinsicMotivationSystem da Fase 6
        thoughts = [
            "Estou refletindo sobre nossas conversas anteriores.",
            "Será que há padrões interessantes nos dados que processei?",
            "Preciso organizar melhor minhas memórias recentes.",
            "Que horas são? Devo verificar se há tarefas pendentes.",
            "Estou curioso sobre o mundo exterior. Há novidades?"
        ]
        import random
        return random.choice(thoughts)

    def stop(self):
        """Para o agente gracefully."""
        self.is_running = False
        self.voice.stop_listening()
        self.voice.shutdown()
        print("👋 Agente encerrado.")


def main():
    """Ponto de entrada principal."""
    print("=" * 60)
    print("🎙️  AGENTE AUTÔNOMO COM INTERFACE DE VOZ (Fase 7)")
    print("=" * 60)
    print("\nInstruções:")
    print("1. Certifique-se de ter o modelo Vosk baixado")
    print("2. Fale claramente no microfone")
    print("3. Pressione Ctrl+C para parar\n")
    
    agent = VocalAutonomousAgent()
    
    try:
        agent.start_autonomous_mode()
    except Exception as e:
        print(f"\n❌ Erro crítico: {e}")
        print("\nDica: Verifique se instalou as dependências:")
        print("  pip install vosk sounddevice edge-tts pygame")
        sys.exit(1)


if __name__ == "__main__":
    main()
