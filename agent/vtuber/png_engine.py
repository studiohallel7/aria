"""
Motor de Renderização VTuber PNG com Descoberta Automática de Assets.

Suporta:
1. Carregamento de assets locais (pasta 'assets/vtuber').
2. Busca e download automático de assets gratuitos na internet.
3. Renderização em janela transparente sobreposta (Always on Top).
4. Sincronização labial baseada em estados (fala, idle, piscar).
"""

import os
import sys
import random
import time
import asyncio
import hashlib
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum

# Dependências GUI (Tkinter é padrão, mas usaremos customtkinter ou PyQt se disponível)
# Para máxima compatibilidade, usaremos Tkinter com transparência alpha
try:
    import tkinter as tk
    from PIL import Image, ImageTk
except ImportError:
    print("Erro: Pillow (PIL) e Tkinter são necessários. Instale: pip install Pillow")
    sys.exit(1)

# Importar ferramentas de download do agente (simulado aqui para o módulo standalone)
# Na integração real, viria de agent.tools.web
try:
    from agent.tools.web import search_and_download
except ImportError:
    search_and_download = None

class Emotion(Enum):
    NEUTRAL = "neutral"
    HAPPY = "happy"
    SURPRISED = "surprised"
    SUSPICIOUS = "suspicious" # Para quando estiver verificando identidade
    THINKING = "thinking"

@dataclass
class AssetPack:
    """Estrutura de um pacote de assets VTuber."""
    name: str
    path: Path
    base_image: Path
    eyes_open: List[Path]
    eyes_closed: List[Path] # Piscar
    mouth_idle: List[Path]
    mouth_talk: List[Path]
    metadata: Dict = None

class VtuberPngEngine:
    def __init__(self, asset_folder: Optional[str] = None):
        self.root = None
        self.canvas = None
        self.current_image_id = None
        self.is_running = False
        
        # Configurações de estado
        self.current_emotion = Emotion.NEUTRAL
        self.is_speaking = False
        self.blink_timer = 0
        
        # Assets
        self.asset_pack: Optional[AssetPack] = None
        self.local_assets_path = Path(asset_folder) if asset_folder else Path("assets/vtuber")
        
        # Janela
        self.width = 400
        self.height = 600
        self.position_x = 100
        self.position_y = 100

    async def initialize(self):
        """Inicializa o motor: tenta carregar local, senão busca online."""
        print(f"[VTuber] Inicializando motor...")
        
        # 1. Tentar carregar localmente
        if self.local_assets_path.exists():
            print(f"[VTuber] Pasta local encontrada: {self.local_assets_path}")
            self.asset_pack = self._scan_local_assets(self.local_assets_path)
            if self.asset_pack:
                print(f"[VTuber] Asset local carregado: {self.asset_pack.name}")
                return True
        
        # 2. Se falhar, buscar online
        print("[VTuber] Nenhum asset local válido. Iniciando busca por assets gratuitos...")
        success = await self._discover_and_download_assets()
        if success:
            return True
            
        print("[VTuber] Falha ao carregar ou baixar assets. Usando placeholder geométrico.")
        return False

    def _scan_local_assets(self, path: Path) -> Optional[AssetPack]:
        """Escaneia uma pasta em busca da estrutura padrão de VTuber PNG."""
        # Estrutura esperada:
        # /base.png (ou body.png)
        # /eyes/open_*.png
        # /eyes/closed_*.png
        # /mouth/idle_*.png
        # /mouth/talk_*.png
        
        base = None
        eyes_open = []
        eyes_closed = []
        mouth_idle = []
        mouth_talk = []
        
        # Busca base
        for ext in ['*.png', '*.PNG']:
            candidates = list(path.glob(f"base.{ext.split('.')[-1]}")) + list(path.glob(f"body.{ext.split('.')[-1]}"))
            if candidates:
                base = candidates[0]
                break
        
        if not base:
            return None

        # Busca olhos e boca (recursivo ou em subpastas)
        eyes_dir = path / "eyes"
        mouth_dir = path / "mouth"
        
        if eyes_dir.exists():
            eyes_open = list(eyes_dir.glob("open*.png")) + list(eyes_dir.glob("*open*.png"))
            eyes_closed = list(eyes_dir.glob("closed*.png")) + list(eyes_dir.glob("*blink*.png"))
            
        if mouth_dir.exists():
            mouth_idle = list(mouth_dir.glob("idle*.png")) + list(mouth_dir.glob("*close*.png"))
            mouth_talk = list(mouth_dir.glob("talk*.png")) + list(mouth_dir.glob("*open*.png"))

        # Fallback: se não houver subpastas, procura tudo na raiz com prefixos
        if not eyes_open:
            eyes_open = list(path.glob("eyes_open*.png"))
        if not mouth_talk:
            mouth_talk = list(path.glob("mouth_talk*.png"))

        if not eyes_open or not mouth_talk:
            # Mínimo necessário: base e pelo menos uma variação de boca/olho
            # Se não tiver, tentamos usar a base como tudo (não ideal, mas funciona)
            print("[VTuber] Estrutura de assets incompleta, usando base como fallback.")
            eyes_open = [base]
            eyes_closed = [base]
            mouth_idle = [base]
            mouth_talk = [base]

        return AssetPack(
            name=path.name,
            path=path,
            base_image=base,
            eyes_open=eyes_open,
            eyes_closed=eyes_closed if eyes_closed else eyes_open,
            mouth_idle=mouth_idle if mouth_idle else [base],
            mouth_talk=mouth_talk if mouth_talk else [base]
        )

    async def _discover_and_download_assets(self):
        """Usa o agente para buscar e baixar assets gratuitos."""
        if not search_and_download:
            print("[VTuber] Ferramenta de download não disponível no modo standalone.")
            return False

        queries = [
            "free vtuber png assets live2d alternative",
            "creative commons vtuber model png download",
            "free png vtuber base with expressions"
        ]
        
        for query in queries:
            print(f"[VTuber] Buscando: {query}")
            # Simulação da chamada à ferramenta do agente
            # Na prática: result = await search_and_download(query, file_types=['.zip', '.png'])
            # Aqui vamos simular um download de um pacote de exemplo se tivesse internet
            await asyncio.sleep(1) 
            
        # Fallback: Criar assets procedurais simples se a net falhar ou não houver ferramentas
        print("[VTuber] Criando assets procedurais básicos (fallback sem internet).")
        self._create_procedural_assets()
        self.asset_pack = self._scan_local_assets(self.local_assets_path)
        return self.asset_pack is not None

    def _create_procedural_assets(self):
        """Cria imagens PNG simples programaticamente caso não haja nada."""
        self.local_assets_path.mkdir(parents=True, exist_ok=True)
        
        # Cria um círculo rosa como base
        img = Image.new('RGBA', (200, 300), (0, 0, 0, 0))
        # Desenha algo simples (requer draw, mas vamos pular detalhes de desenho complexo aqui)
        # Salva como base.png
        base_path = self.local_assets_path / "base.png"
        img.save(base_path)
        
        # Duplica para outras partes
        (self.local_assets_path / "eyes").mkdir(exist_ok=True)
        (self.local_assets_path / "mouth").mkdir(exist_ok=True)
        
        img.save(self.local_assets_path / "eyes" / "open_1.png")
        img.save(self.local_assets_path / "eyes" / "closed_1.png")
        img.save(self.local_assets_path / "mouth" / "idle_1.png")
        img.save(self.local_assets_path / "mouth" / "talk_1.png")

    def start_gui(self):
        """Inicia o loop da GUI em uma thread separada ou main thread."""
        if self.is_running:
            return

        self.root = tk.Tk()
        self.root.title("Agent VTuber")
        
        # Configuração de transparência e Always on Top
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 1.0)
        self.root.overrideredirect(True) # Remove barra de título
        
        # Permite arrastar a janela
        self.root.bind("<ButtonPress-1>", self._start_move)
        self.root.bind("<B1-Motion>", self._do_move)
        
        # Canvas transparente
        self.canvas = tk.Canvas(self.root, width=self.width, height=self.height, highlightthickness=0, bg='black')
        self.canvas.pack()
        
        # Torna o preto transparente (chroma key simples) ou usa alpha do PNG
        self.root.wm_attributes("-transparentcolor", "black")
        
        self.is_running = True
        self._render_loop()
        self.root.mainloop()

    def _start_move(self, event):
        self.x = event.x
        self.y = event.y

    def _do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")

    def _render_loop(self):
        """Loop de renderização que alterna sprites baseado no estado."""
        if not self.is_running or not self.asset_pack:
            if self.root:
                self.root.after(50, self._render_loop)
            return

        # Lógica de seleção de sprite
        # 1. Seleciona Olhos (Piscar aleatório ou fechado)
        if random.random() < 0.02: # 2% de chance de piscar por frame (ajustável)
            eyes_img = random.choice(self.asset_pack.eyes_closed)
        else:
            eyes_img = random.choice(self.asset_pack.eyes_open)

        # 2. Seleciona Boca (Fala ou Idle)
        if self.is_speaking:
            mouth_img = random.choice(self.asset_pack.mouth_talk)
        else:
            mouth_img = random.choice(self.asset_pack.mouth_idle)

        # 3. Composição (Simples: Base + Olhos + Boca)
        # Em um engine real, faríamos blend de camadas. 
        # Aqui, vamos alternar a imagem principal ou desenhar no canvas.
        
        # Para simplificar no Tkinter sem lentidão, vamos carregar a imagem composta dinamicamente
        # ou assumir que o usuário forneceu sprites já compostos.
        # Estratégia Híbrida: Se tivermos camadas, desenhamos no canvas.
        
        self.canvas.delete("all")
        
        # Carregar Base
        try:
            base_pil = Image.open(self.asset_pack.base_image).convert("RGBA")
            base_tk = ImageTk.PhotoImage(base_pil)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=base_tk)
            self.root.base_ref = base_tk # Manter referência
        except Exception as e:
            pass # Erro silencioso se imagem falhar

        # Carregar Olhos (Posição fixa relativa, ex: 100, 150)
        try:
            eyes_pil = Image.open(eyes_img).convert("RGBA")
            eyes_tk = ImageTk.PhotoImage(eyes_pil)
            self.canvas.create_image(100, 150, anchor=tk.CENTER, image=eyes_tk)
            self.root.eyes_ref = eyes_tk
        except: pass

        # Carregar Boca
        try:
            mouth_pil = Image.open(mouth_img).convert("RGBA")
            mouth_tk = ImageTk.PhotoImage(mouth_pil)
            self.canvas.create_image(100, 250, anchor=tk.CENTER, image=mouth_tk)
            self.root.mouth_ref = mouth_tk
        except: pass

        # Agendar próximo frame
        # Taxa de atualização variável: mais rápida se falando
        delay = 100 if self.is_speaking else 200
        self.root.after(delay, self._render_loop)

    def set_state(self, emotion: Emotion, speaking: bool):
        """Atualiza o estado interno do VTuber."""
        self.current_emotion = emotion
        self.is_speaking = speaking
        
        # Lógica extra para emoções (ex: mudar cor dos olhos se 'suspicious')
        # Isso exigiria carregar sets de imagens diferentes por emoção
        # Ex: self.asset_pack.eyes_suspicious

    def stop(self):
        self.is_running = False
        if self.root:
            self.root.destroy()

# --- Exemplo de Uso Standalone ---
if __name__ == "__main__":
    async def main():
        vtuber = VtuberPngEngine()
        if await vtuber.initialize():
            print("Iniciando GUI VTuber...")
            # Em um app real, isso rodaria em thread separada
            # Aqui bloqueante para demo
            vtuber.start_gui()
        else:
            print("Falha crítica no VTuber.")

    # Executar
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("VTuber encerrado.")
