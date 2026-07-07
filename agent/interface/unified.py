"""
Interface Unificada do Agente - Chat, Voz, GUI e Modo VTuber
Integra todas as interfaces em um único sistema coeso com seleção de modo.

Modos disponíveis:
- chat: Interface de texto tradicional (CLI)
- voice: Interface por voz (Vosk + EdgeTTS)
- gui: Dashboard gráfico (Streamlit)
- vtuber: Avatar animado com sincronização labial (Live2D/VRM)
- unified: Todos os modos ativos simultaneamente
"""

import asyncio
import threading
import queue
import time
import json
import os
import sys
from typing import Optional, Callable, Dict, Any, List
from enum import Enum
from dataclasses import dataclass, field

# Imports das interfaces existentes
try:
    from agent.interface.voice import VoiceInterface
    VOICE_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False
    print("⚠️  VoiceInterface não disponível")

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

try:
    import cv2
    import numpy as np
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False


class InterfaceMode(Enum):
    """Modos de interface disponíveis."""
    CHAT = "chat"
    VOICE = "voice"
    GUI = "gui"
    VTUBER = "vtuber"
    UNIFIED = "unified"


@dataclass
class Message:
    """Estrutura de mensagem unificada."""
    content: str
    source: str = "user"  # user, agent, system
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)


class VTuberAvatar:
    """
    Gerenciador de Avatar VTuber.
    Suporta modelos VRM/Live2D baixáveis da internet.
    """
    
    # URLs de modelos gratuitos populares
    FREE_MODELS = {
        "vrm_default": "https://github.com/vrm-c/Free3DModels/archive/main.zip",
        "live2d_default": "https://cubism.live2d.com/sample-model/",
        "beryl": "https://booth.pm/ja/items/3105959",  # Modelo gratuito popular
    }
    
    def __init__(self, model_path: Optional[str] = None, model_type: str = "vrm"):
        """
        Inicializa o avatar VTuber.
        
        Args:
            model_path: Caminho para o arquivo do modelo (.vrm, .live2d.json)
            model_type: Tipo do modelo ('vrm' ou 'live2d')
        """
        self.model_path = model_path
        self.model_type = model_type
        self.is_loaded = False
        self.expression_queue = queue.Queue()
        self.lip_sync_active = False
        
        # Estado do avatar
        self.current_expression = "neutral"
        self.eye_blink_rate = 0.3  # Piscada a cada 3 segundos
        self.head_rotation = (0.0, 0.0)  # (yaw, pitch)
        
        # Thread de animação
        self.animation_thread: Optional[threading.Thread] = None
        self.is_running = False
        
        if PYGAME_AVAILABLE:
            pygame.init()
            self.screen = None
            self.clock = None
            
        print(f"🎭 VTuber Avatar inicializado (Tipo: {model_type})")
    
    def download_model(self, model_name: str = "vrm_default") -> bool:
        """
        Baixa um modelo pré-configurado da internet.
        
        Args:
            model_name: Nome do modelo na lista FREE_MODELS
            
        Returns:
            True se sucesso, False caso contrário
        """
        if model_name not in self.FREE_MODELS:
            print(f"❌ Modelo '{model_name}' não encontrado na lista de modelos gratuitos")
            return False
        
        url = self.FREE_MODELS[model_name]
        print(f"📥 Baixando modelo {model_name} de: {url}")
        
        try:
            import requests
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            # Salva em diretório de modelos
            models_dir = os.path.join(os.path.dirname(__file__), "..", "..", "models", "vtuber")
            os.makedirs(models_dir, exist_ok=True)
            
            filename = f"{model_name}.{self.model_type}"
            filepath = os.path.join(models_dir, filename)
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            self.model_path = filepath
            print(f"✅ Modelo baixado em: {filepath}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao baixar modelo: {e}")
            return False
    
    def load_model(self, model_path: Optional[str] = None) -> bool:
        """
        Carrega o modelo do avatar.
        
        Args:
            model_path: Caminho opcional para o modelo
            
        Returns:
            True se carregado com sucesso
        """
        path = model_path or self.model_path
        
        if not path:
            print("❌ Nenhum caminho de modelo especificado")
            return False
        
        if not os.path.exists(path):
            print(f"❌ Arquivo de modelo não encontrado: {path}")
            # Oferece para baixar um modelo gratuito
            print("💡 Deseja baixar um modelo gratuito? Use: avatar.download_model('vrm_default')")
            return False
        
        print(f"📦 Carregando modelo: {path}")
        
        # Simulação de carregamento (implementação real depende da biblioteca)
        # Para VRM: usar pyvrm ou vrm-python
        # Para Live2D: usar cubism-sdk ou live2d-py
        
        self.is_loaded = True
        print(f"✅ Modelo carregado: {os.path.basename(path)}")
        return True
    
    def start_animation(self):
        """Inicia o loop de animação do avatar."""
        if not self.is_loaded:
            print("❌ Carregue um modelo antes de iniciar a animação")
            return
        
        self.is_running = True
        self.animation_thread = threading.Thread(target=self._animation_loop, daemon=True)
        self.animation_thread.start()
        print("🎬 Animação do avatar iniciada")
    
    def stop_animation(self):
        """Para o loop de animação."""
        self.is_running = False
        if self.animation_thread:
            self.animation_thread.join(timeout=2.0)
        print("⏹️  Animação parada")
    
    def _animation_loop(self):
        """Loop principal de animação do avatar."""
        last_blink = time.time()
        
        while self.is_running:
            current_time = time.time()
            
            # Processa fila de expressões
            try:
                expression = self.expression_queue.get_nowait()
                self.current_expression = expression
            except queue.Empty:
                pass
            
            # Piscada automática
            if current_time - last_blink > self.eye_blink_rate:
                self._trigger_blink()
                last_blink = current_time
            
            # Sincronização labial (se ativo)
            if self.lip_sync_active:
                self._update_lip_sync()
            
            # Movimento sutil da cabeça
            self._idle_head_movement()
            
            # Renderiza frame (implementação dependente de backend)
            self._render_frame()
            
            time.sleep(1/60)  # 60 FPS
    
    def _trigger_blink(self):
        """Aciona animação de piscada."""
        # Implementação específica do motor de renderização
        pass
    
    def _update_lip_sync(self):
        """Atualiza sincronização labial baseada no áudio."""
        # Implementação específica do motor de renderização
        pass
    
    def _idle_head_movement(self):
        """Movimento sutil da cabeça quando ocioso."""
        import math
        t = time.time()
        self.head_rotation = (
            math.sin(t * 0.5) * 5.0,  # Yaw ±5 graus
            math.cos(t * 0.3) * 3.0   # Pitch ±3 graus
        )
    
    def _render_frame(self):
        """Renderiza um frame do avatar."""
        # Implementação real usaria:
        # - Pygame para janela 2D
        # - PyOpenGL para renderização 3D
        # - Ou integração com Unity/Unreal via rede
        pass
    
    def set_expression(self, expression: str):
        """
        Define expressão facial do avatar.
        
        Args:
            expression: Nome da expressão ('neutral', 'happy', 'sad', 'angry', 'surprised', etc.)
        """
        valid_expressions = ['neutral', 'happy', 'sad', 'angry', 'surprised', 
                           'thinking', 'talking', 'listening']
        if expression in valid_expressions:
            self.expression_queue.put(expression)
        else:
            print(f"⚠️  Expressão '{expression}' não suportada")
    
    def enable_lip_sync(self, audio_stream):
        """
        Ativa sincronização labial com stream de áudio.
        
        Args:
            audio_stream: Stream de áudio para análise em tempo real
        """
        self.lip_sync_active = True
        # Implementação real analisaria amplitudes do áudio
    
    def disable_lip_sync(self):
        """Desativa sincronização labial."""
        self.lip_sync_active = False


class UnifiedInterface:
    """
    Interface Unificada que gerencia todos os modos de interação.
    
    Permite alternar entre modos ou executar múltiplos simultaneamente.
    """
    
    def __init__(self, mode: InterfaceMode = InterfaceMode.CHAT):
        """
        Inicializa a interface unificada.
        
        Args:
            mode: Modo inicial da interface
        """
        self.mode = mode
        self.is_running = False
        self.message_queue = queue.Queue()
        self.response_callbacks: List[Callable[[str], None]] = []
        
        # Componentes de interface
        self.voice_interface: Optional[VoiceInterface] = None
        self.vtuber_avatar: Optional[VTuberAvatar] = None
        self.gui_process: Optional[threading.Thread] = None
        
        # Estado atual
        self.current_mode = mode
        self.available_modes = []
        
        # Detecta capacidades do sistema
        self._detect_capabilities()
        
        print(f"🖥️  Interface Unificada inicializada (Modo: {mode.value})")
    
    def _detect_capabilities(self):
        """Detecta quais interfaces estão disponíveis no sistema."""
        self.available_modes = [InterfaceMode.CHAT]  # CLI sempre disponível
        
        if VOICE_AVAILABLE:
            self.available_modes.append(InterfaceMode.VOICE)
            print("✓ Interface de voz disponível")
        
        try:
            import streamlit
            self.available_modes.append(InterfaceMode.GUI)
            print("✓ Interface GUI disponível")
        except ImportError:
            pass
        
        if OPENCV_AVAILABLE and PYGAME_AVAILABLE:
            self.available_modes.append(InterfaceMode.VTUBER)
            print("✓ Modo VTuber disponível")
        
        if len(self.available_modes) > 1:
            self.available_modes.append(InterfaceMode.UNIFIED)
    
    def initialize_components(self):
        """Inicializa todos os componentes necessários para o modo atual."""
        if self.current_mode in [InterfaceMode.VOICE, InterfaceMode.UNIFIED]:
            if VOICE_AVAILABLE:
                self.voice_interface = VoiceInterface()
                self.voice_interface.on_speech_detected = self._on_voice_input
                print("🎙️  Interface de voz pronta")
        
        if self.current_mode in [InterfaceMode.VTUBER, InterfaceMode.UNIFIED]:
            self.vtuber_avatar = VTuberAvatar()
            print("🎭 Avatar VTuber pronto")
    
    def start(self):
        """Inicia a interface no modo selecionado."""
        self.is_running = True
        self.initialize_components()
        
        print(f"\n{'='*60}")
        print(f"🚀 Iniciando Interface no modo: {self.current_mode.value.upper()}")
        print(f"{'='*60}\n")
        
        if self.current_mode == InterfaceMode.CHAT:
            self._start_chat_mode()
        elif self.current_mode == InterfaceMode.VOICE:
            self._start_voice_mode()
        elif self.current_mode == InterfaceMode.GUI:
            self._start_gui_mode()
        elif self.current_mode == InterfaceMode.VTUBER:
            self._start_vtuber_mode()
        elif self.current_mode == InterfaceMode.UNIFIED:
            self._start_unified_mode()
    
    def _start_chat_mode(self):
        """Inicia modo de chat CLI."""
        print("💬 MODO CHAT ATIVADO")
        print("Digite suas mensagens (ou 'sair' para encerrar)\n")
        
        while self.is_running:
            try:
                user_input = input("Você: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['sair', 'exit', 'quit']:
                    self.stop()
                    break
                
                # Processa entrada
                self._process_user_message(user_input, source="chat")
                
            except KeyboardInterrupt:
                self.stop()
                break
            except EOFError:
                self.stop()
                break
    
    def _start_voice_mode(self):
        """Inicia modo de voz."""
        if not self.voice_interface:
            print("❌ Interface de voz não inicializada")
            return
        
        print("🎙️  MODO VOZ ATIVADO")
        print("Fale naturalmente. O agente responderá por voz.\n")
        
        # Configura callback de resposta
        def on_agent_response(text: str):
            print(f"🤖 Agente: {text}")
            self.voice_interface.speak(text)
            if self.vtuber_avatar:
                self.vtuber_avatar.set_expression("talking")
        
        self.response_callbacks.append(on_agent_response)
        
        # Inicia escuta
        self.voice_interface.start_listening(self._on_voice_input)
        
        # Mantém thread principal viva
        try:
            while self.is_running:
                time.sleep(0.1)
        except KeyboardInterrupt:
            self.stop()
    
    def _start_gui_mode(self):
        """Inicia modo GUI (Streamlit)."""
        print("🖥️  MODO GUI ATIVADO")
        print("Iniciando dashboard Streamlit...\n")
        
        def run_streamlit():
            os.system("streamlit run agent/ui/dashboard.py --server.headless true")
        
        self.gui_process = threading.Thread(target=run_streamlit, daemon=True)
        self.gui_process.start()
        
        print("Dashboard disponível em http://localhost:8501")
        print("Pressione Ctrl+C para parar\n")
        
        try:
            while self.is_running:
                time.sleep(0.1)
        except KeyboardInterrupt:
            self.stop()
    
    def _start_vtuber_mode(self):
        """Inicia modo VTuber."""
        if not self.vtuber_avatar:
            print("❌ Avatar VTuber não inicializado")
            return
        
        print("🎭 MODO VTUBER ATIVADO")
        print("Carregue um modelo para começar\n")
        
        # Tenta carregar modelo padrão
        if not self.vtuber_avatar.is_loaded:
            # Oferece download de modelo gratuito
            print("Nenhum modelo carregado. Deseja baixar um modelo gratuito?")
            choice = input("Baixar modelo padrão? (s/n): ").strip().lower()
            if choice == 's':
                if self.vtuber_avatar.download_model("vrm_default"):
                    self.vtuber_avatar.load_model()
        
        if self.vtuber_avatar.is_loaded:
            self.vtuber_avatar.start_animation()
            
            # Combina com chat ou voz
            print("\nModo VTuber ativo. Combine com:")
            print("  1. Chat (digite texto)")
            print("  2. Voz (fale no microfone)")
            
            choice = input("\nEscolha (1-2): ").strip()
            if choice == "1":
                self._start_chat_mode()
            elif choice == "2":
                self._start_voice_mode()
        else:
            print("⚠️  Continuando sem avatar...")
            self._start_chat_mode()
    
    def _start_unified_mode(self):
        """Inicia todos os modos simultaneamente."""
        print("🌟 MODO UNIFICADO ATIVADO")
        print("Todos os sistemas online: Chat + Voz + GUI + VTuber\n")
        
        # Inicia GUI em background
        if InterfaceMode.GUI in self.available_modes:
            self._start_gui_mode()
        
        # Inicia VTuber
        if self.vtuber_avatar and self.vtuber_avatar.is_loaded:
            self.vtuber_avatar.start_animation()
        
        # Inicia voz
        if self.voice_interface:
            self.voice_interface.start_listening(self._on_voice_input)
        
        # Loop principal de chat
        print("\nSistemas ativos:")
        print("  ✓ Chat (digite)")
        print("  ✓ Voz (fale)")
        print("  ✓ GUI (navegador)")
        print("  ✓ VTuber (avatar)")
        print("\nDigite 'modo <nome>' para mudar ou 'sair' para encerrar\n")
        
        while self.is_running:
            try:
                user_input = input("Você: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['sair', 'exit', 'quit']:
                    self.stop()
                    break
                
                # Comandos especiais
                if user_input.startswith('modo '):
                    new_mode = user_input.split()[1].lower()
                    self.switch_mode(new_mode)
                    continue
                
                self._process_user_message(user_input, source="unified")
                
            except KeyboardInterrupt:
                self.stop()
                break
    
    def _on_voice_input(self, text: str):
        """Callback para entrada de voz."""
        print(f"👂 Ouvi: '{text}'")
        self._process_user_message(text, source="voice")
        
        # Reativa escuta após processamento
        if self.voice_interface and self.is_running:
            self.voice_interface.start_listening(self._on_voice_input)
    
    def _process_user_message(self, text: str, source: str = "user"):
        """
        Processa mensagem do usuário e gera resposta.
        
        Args:
            text: Conteúdo da mensagem
            source: Origem (chat, voice, etc.)
        """
        print(f"💬 [{source}] Usuário: {text}")
        
        # Atualiza expressão do VTuber
        if self.vtuber_avatar:
            self.vtuber_avatar.set_expression("listening")
        
        # Aqui entraria a lógica real do agente
        # Por enquanto, resposta simulada
        response = self._generate_response(text)
        
        # Dispara callbacks de resposta
        for callback in self.response_callbacks:
            callback(response)
        
        # Se não houver callbacks específicos, usa output padrão
        if not self.response_callbacks:
            print(f"🤖 Agente: {response}")
            
            # Fala se tiver interface de voz
            if self.voice_interface:
                self.voice_interface.speak(response)
            
            # Atualiza VTuber
            if self.vtuber_avatar:
                self.vtuber_avatar.set_expression("talking")
                time.sleep(len(response) * 0.1)  # Tempo estimado de fala
                self.vtuber_avatar.set_expression("neutral")
    
    def _generate_response(self, text: str) -> str:
        """
        Gera resposta baseada na entrada.
        (Substituir por chamada real ao LLM)
        """
        text_lower = text.lower()
        
        if "olá" in text_lower or "oi" in text_lower:
            return "Olá! Como posso ajudar você hoje?"
        
        if "como está" in text_lower:
            return "Estou funcionando perfeitamente! E você?"
        
        if "modo" in text_lower:
            modes = ", ".join([m.value for m in self.available_modes])
            return f"Modos disponíveis: {modes}. Digite 'modo <nome>' para trocar."
        
        if "vtuber" in text_lower:
            return "Sou capaz de exibir um avatar animado! Carregue um modelo VRM ou Live2D."
        
        return f"Entendi: '{text}'. Estou processando sua solicitação."
    
    def switch_mode(self, mode_name: str):
        """
        Alterna para outro modo de interface.
        
        Args:
            mode_name: Nome do modo desejado
        """
        try:
            new_mode = InterfaceMode(mode_name.lower())
            
            if new_mode not in self.available_modes:
                print(f"❌ Modo '{mode_name}' não disponível neste sistema")
                return
            
            print(f"\n🔄 Alternando para modo: {new_mode.value}\n")
            
            # Para componentes atuais
            if self.voice_interface:
                self.voice_interface.stop_listening()
            if self.vtuber_avatar:
                self.vtuber_avatar.stop_animation()
            
            # Muda modo e reinicia
            self.current_mode = new_mode
            self.start()
            
        except ValueError:
            print(f"❌ Modo inválido: {mode_name}")
            available = ", ".join([m.value for m in self.available_modes])
            print(f"Modos disponíveis: {available}")
    
    def send_message(self, content: str, source: str = "system"):
        """
        Envia mensagem através da interface unificada.
        
        Args:
            content: Conteúdo da mensagem
            source: Origem da mensagem
        """
        message = Message(content=content, source=source)
        self.message_queue.put(message)
    
    def add_response_callback(self, callback: Callable[[str], None]):
        """
        Adiciona callback para respostas do agente.
        
        Args:
            callback: Função que recebe o texto da resposta
        """
        self.response_callbacks.append(callback)
    
    def stop(self):
        """Encerra todos os componentes da interface."""
        print("\n⏹️  Encerrando interface...")
        
        self.is_running = False
        
        if self.voice_interface:
            self.voice_interface.shutdown()
        
        if self.vtuber_avatar:
            self.vtuber_avatar.stop_animation()
        
        print("👋 Interface encerrada.")


def create_interface(mode: str = "chat") -> UnifiedInterface:
    """
    Factory function para criar interface.
    
    Args:
        mode: Modo desejado ('chat', 'voice', 'gui', 'vtuber', 'unified')
        
    Returns:
        Instância de UnifiedInterface
    """
    try:
        interface_mode = InterfaceMode(mode.lower())
        return UnifiedInterface(interface_mode)
    except ValueError:
        print(f"⚠️  Modo '{mode}' não reconhecido. Usando 'chat'.")
        return UnifiedInterface(InterfaceMode.CHAT)


def main():
    """Ponto de entrada principal."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Interface Unificada do Agente - Chat, Voz, GUI e VTuber"
    )
    parser.add_argument(
        "--mode", "-m",
        type=str,
        default="chat",
        choices=["chat", "voice", "gui", "vtuber", "unified"],
        help="Modo de interface (padrão: chat)"
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Caminho para modelo VTuber (.vrm ou .live2d.json)"
    )
    parser.add_argument(
        "--voice",
        type=str,
        default="pt-BR-FranciscaNeural",
        help="Nome da voz para TTS (EdgeTTS)"
    )
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("🤖 INTERFACE UNIFICADA DO AGENTE")
    print("Modos: Chat • Voz • GUI • VTuber • Unificado")
    print("=" * 70)
    
    # Cria interface
    interface = create_interface(args.mode)
    
    # Configura modelo VTuber se fornecido
    if args.model and interface.vtuber_avatar:
        interface.vtuber_avatar.model_path = args.model
    
    # Inicia
    try:
        interface.start()
    except KeyboardInterrupt:
        print("\n\nInterrompido pelo usuário.")
    except Exception as e:
        print(f"\n❌ Erro crítico: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
