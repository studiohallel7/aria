"""
Interface de Voz Nativa (Fase 7)
Integra Vosk (STT) e EdgeTTS (TTS) para interação natural.
Baseado na implementação fornecida pelo usuário.
"""
import asyncio
import edge_tts
import pygame
import tempfile
import threading
import os
import json
import queue
import sys
from typing import Callable, Optional
import sounddevice as sd

try:
    from vosk import Model, KaldiRecognizer
    VOSK_AVAILABLE = True
except ImportError:
    VOSK_AVAILABLE = False
    print("⚠️  Vosk não instalado. Execute: pip install vosk")

class VoiceInterface:
    """
    Controlador de Voz Bidirecional.
    - Escuta via microfone (Vosk)
    - Fala via sintetizador neural (EdgeTTS)
    - Funciona em threads separadas para não bloquear o loop do agente.
    """
    
    def __init__(self, voice_name: str = "pt-BR-FranciscaNeural"):
        pygame.mixer.init()
        self.voice_name = voice_name
        self.q = queue.Queue()
        self.vosk_model: Optional[Model] = None
        self.is_listening = False
        self.listening_thread: Optional[threading.Thread] = None
        
        # Callbacks
        self.on_speech_detected: Optional[Callable[[str], None]] = None
        self.on_error: Optional[Callable[[str], None]] = None
        
        # Pipelined TTS (Gerador e Player separados)
        self.text_queue = queue.Queue()
        self.audio_queue = queue.Queue()
        
        self.worker_gen = threading.Thread(target=self._tts_generator_worker, daemon=True)
        self.worker_play = threading.Thread(target=self._tts_player_worker, daemon=True)
        self.worker_gen.start()
        self.worker_play.start()
        
        print(f"🎙️  Interface de Voz inicializada (Voz: {voice_name})")

    def load_vosk_model(self) -> bool:
        """Carrega o modelo Vosk localmente."""
        if not VOSK_AVAILABLE:
            return False
            
        if self.vosk_model:
            return True
            
        # Tenta encontrar o modelo em caminhos comuns
        possible_paths = [
            os.path.join(os.path.dirname(__file__), "..", "..", "model", "pt"),
            os.path.join(os.getcwd(), "model", "pt"),
            os.path.expanduser("~/.vosk-models/pt"),
            "model/pt"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                try:
                    print(f"📥 Carregando modelo Vosk de: {path} ...")
                    self.vosk_model = Model(path)
                    print("✅ Modelo Vosk carregado com sucesso.")
                    return True
                except Exception as e:
                    print(f"❌ Erro ao carregar modelo em {path}: {e}")
        
        msg = "⚠️  Modelo Vosk não encontrado. Baixe em: https://alphacephei.com/vosk/models"
        print(msg)
        if self.on_error:
            self.on_error(msg)
        return False

    def start_listening(self, callback: Callable[[str], None]):
        """Inicia a escuta em background thread."""
        self.on_speech_detected = callback
        
        if not self.load_vosk_model():
            if self.on_error:
                self.on_error("STT indisponível: Modelo Vosk faltando.")
            return

        self.is_listening = True
        self.listening_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.listening_thread.start()

    def stop_listening(self):
        """Para a escuta."""
        self.is_listening = False
        if self.listening_thread:
            self.listening_thread.join(timeout=2.0)

    def _listen_loop(self):
        """Loop interno de captura de áudio."""
        rec = KaldiRecognizer(self.vosk_model, 16000)
        
        def audio_callback(indata, frames, time, status):
            if status:
                print(status, file=sys.stderr)
            self.q.put(bytes(indata))

        try:
            with sd.RawInputStream(samplerate=16000, blocksize=8000, device=None, 
                                   dtype='int16', channels=1, callback=audio_callback):
                while self.is_listening:
                    data = self.q.get()
                    if rec.AcceptWaveform(data):
                        res = json.loads(rec.Result())
                        text = res.get("text", "")
                        if text and text.strip():
                            print(f"👂 Ouvi: '{text}'")
                            if self.on_speech_detected:
                                # Executa callback no thread principal ou direto
                                self.on_speech_detected(text)
                            self.is_listening = False # Para após uma frase (push-to-talk style ou pause detection)
                            break
        except Exception as e:
            err_msg = f"Erro no microfone: {e}"
            print(err_msg)
            if self.on_error:
                self.on_error(err_msg)
            self.is_listening = False

    def speak(self, text: str):
        """Adiciona texto à fila de fala."""
        if not text or not text.strip():
            return
        self.text_queue.put(text)

    def _tts_generator_worker(self):
        """Worker assíncrono para gerar áudio a partir de texto."""
        while True:
            text = self.text_queue.get()
            if text is None: 
                break

            fd, temp_path = tempfile.mkstemp(suffix=".mp3")
            os.close(fd)

            async def _generate():
                communicate = edge_tts.Communicate(text, self.voice_name)
                await communicate.save(temp_path)

            try:
                asyncio.run(_generate())
                self.audio_queue.put(temp_path)
            except Exception as e:
                print(f"❌ Erro TTS: {e}")
                if self.on_error:
                    self.on_error(f"Falha na síntese de voz: {e}")
            
            self.text_queue.task_done()

    def _tts_player_worker(self):
        """Worker para tocar arquivos de áudio gerados."""
        while True:
            temp_path = self.audio_queue.get()
            if temp_path is None: 
                break

            try:
                pygame.mixer.music.load(temp_path)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)
            except Exception as e:
                print(f"❌ Erro ao reproduzir áudio: {e}")

            try: 
                os.remove(temp_path)
            except: 
                pass

            self.audio_queue.task_done()

    def shutdown(self):
        """Encerra gracefully."""
        self.stop_listening()
        self.text_queue.put(None)
        self.audio_queue.put(None)
        self.worker_gen.join(timeout=2.0)
        self.worker_play.join(timeout=2.0)
        pygame.mixer.quit()
