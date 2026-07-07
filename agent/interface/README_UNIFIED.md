# Interface Unificada do Agente

Este módulo unifica todas as interfaces do agente (CLI, Voz, GUI e VTuber) em um único sistema coeso.

## 🚀 Recursos

### Modos de Interface

1. **Chat (CLI)** - Interface de texto tradicional via terminal
2. **Voice** - Interface por voz usando Vosk (STT) e EdgeTTS (TTS)
3. **GUI** - Dashboard gráfico interativo usando Streamlit
4. **VTuber** - Avatar animado com sincronização labial (VRM/Live2D)
5. **Unified** - Todos os modos ativos simultaneamente

### Modo VTuber

O modo VTuber permite usar avatares animados que reagem às interações:

- **Modelos Suportados**: VRM (3D) e Live2D (2D)
- **Download Automático**: Modelos gratuitos pré-configurados
- **Expressões Faciais**: Neutral, happy, sad, angry, surprised, thinking, talking, listening
- **Sincronização Labial**: Animacao da boca sincronizada com áudio TTS
- **Movimento Natural**: Piscada automática e movimento sutil da cabeça

## 📦 Instalação

### Dependências Básicas

```bash
pip install pygame sounddevice edge-tts click rich
```

### Para Voice Interface

```bash
pip install vosk sounddevice edge-tts pygame
```

Baixe o modelo Vosk para português:
```bash
wget https://alphacephei.com/vosk/models/vosk-model-small-pt-0.3.zip
unzip vosk-model-small-pt-0.3.zip
mv vosk-model-small-pt-0.3 agent/model/pt
```

### Para GUI (Streamlit)

```bash
pip install streamlit plotly pandas
```

### Para VTuber

```bash
pip install opencv-python numpy pygame requests
```

Para suporte completo a modelos VRM:
```bash
pip install pyvrm  # ou vrm-python
```

Para suporte a Live2D:
```bash
# Requer Cubism SDK da Live2D
# Visite: https://www.live2d.com/en/download/cubism-sdk/
```

## 💻 Uso

### Linha de Comando

```bash
# Modo Chat (padrão)
python -m agent.interface.unified --mode chat

# Modo Voz
python -m agent.interface.unified --mode voice

# Modo GUI
python -m agent.interface.unified --mode gui

# Modo VTuber
python -m agent.interface.unified --mode vtuber

# Modo Unificado (todos simultâneos)
python -m agent.interface.unified --mode unified

# Com modelo VTuber personalizado
python -m agent.interface.unified --mode vtuber --model /caminho/para/modelo.vrm

# Com voz personalizada
python -m agent.interface.unified --mode voice --voice pt-BR-FranciscaNeural
```

### Programaticamente

```python
from agent.interface import create_interface, InterfaceMode

# Criar interface no modo unificado
interface = create_interface("unified")

# Adicionar callback para respostas do agente
def on_agent_response(text):
    print(f"Resposta: {text}")

interface.add_response_callback(on_agent_response)

# Iniciar
interface.start()
```

### Usando o VTuberAvatar Diretamente

```python
from agent.interface import VTuberAvatar

# Criar avatar
avatar = VTuberAvatar(model_type="vrm")

# Baixar modelo gratuito
avatar.download_model("vrm_default")

# Carregar modelo
avatar.load_model()

# Iniciar animação
avatar.start_animation()

# Mudar expressão
avatar.set_expression("happy")
avatar.set_expression("talking")

# Parar animação
avatar.stop_animation()
```

## 🎭 Lista de Modelos VTuber Gratuitos

O módulo inclui links para modelos gratuitos:

| Nome | Tipo | URL |
|------|------|-----|
| vrm_default | VRM | GitHub VRM Samples |
| live2d_default | Live2D | Cubism Sample Models |
| beryl | VRM | Booth.pm (gratuito) |

### Como Adicionar Seus Próprios Modelos

1. Baixe modelos VRM de sites como:
   - [Booth.pm](https://booth.pm/)
   - [VRoid Hub](https://hub.vroid.com/)
   - [Sketchfab](https://sketchfab.com/)

2. Coloque o arquivo `.vrm` na pasta `agent/models/vtuber/`

3. Use o caminho ao iniciar:
   ```bash
   python -m agent.interface.unified --mode vtuber --model agent/models/vtuber/meu_modelo.vrm
   ```

## 🔄 Alternando Entre Modos

No modo unificado, você pode alternar entre modos dinamicamente:

```
Digite 'modo chat' para mudar para apenas chat
Digite 'modo voice' para mudar para apenas voz
Digite 'modo gui' para abrir dashboard
Digite 'modo vtuber' para focar no avatar
Digite 'sair' para encerrar
```

## 🏗️ Arquitetura

```
UnifiedInterface
├── VoiceInterface (Vosk + EdgeTTS)
├── VTuberAvatar (VRM/Live2D)
├── GUI Process (Streamlit)
└── Chat CLI (input/output)

Message Flow:
Usuário → Message Queue → Processamento → Response Callbacks → Interfaces
```

## 📝 Exemplos de Uso

### Demo Rápida - Chat

```python
from agent.interface import create_interface

interface = create_interface("chat")
interface.start()
```

### Demo - Voz com Resposta Falada

```python
from agent.interface import create_interface

interface = create_interface("voice")
interface.start()
# Fale no microfone, o agente responderá por voz
```

### Demo - VTuber com Download de Modelo

```python
from agent.interface import VTuberAvatar

avatar = VTuberAvatar()

# Baixa e carrega modelo automaticamente
if avatar.download_model("vrm_default"):
    avatar.load_model()
    avatar.start_animation()
    
    # Testa expressões
    for expr in ["happy", "thinking", "talking", "neutral"]:
        avatar.set_expression(expr)
        time.sleep(2)
    
    avatar.stop_animation()
```

### Demo - Unificado com Callback Personalizado

```python
from agent.interface import create_interface

interface = create_interface("unified")

# Conecta com o cérebro do agente
def process_and_respond(text):
    # Aqui entraria a lógica real do agente
    return f"Processado: {text}"

interface.add_response_callback(process_and_respond)
interface.start()
```

## ⚙️ Configuração Avançada

### Vozes Disponíveis (EdgeTTS)

Português:
- `pt-BR-FranciscaNeural` (feminina)
- `pt-BR-AntonioNeural` (masculina)
- `pt-PT-DuarteNeural` (Portugal)

Inglês:
- `en-US-JennyNeural`
- `en-US-GuyNeural`
- `en-GB-SoniaNeural`

Lista completa: https://github.com/matthuisman/edge-tts

### Personalização do Avatar

```python
avatar = VTuberAvatar()
avatar.eye_blink_rate = 0.5  # Piscar a cada 5 segundos
avatar.head_rotation = (10.0, 5.0)  # Amplitude do movimento da cabeça
```

## 🐛 Solução de Problemas

### Voice Interface não funciona

1. Verifique se o modelo Vosk está baixado
2. Teste o microfone: `arecord -l` (Linux) ou `pyaudio.test()` 
3. Instale dependências: `pip install vosk sounddevice`

### VTuber não carrega modelos

1. Verifique se OpenCV está instalado: `pip install opencv-python`
2. Confirme o caminho do modelo
3. Para VRM, instale: `pip install pyvrm`

### GUI não abre

1. Instale Streamlit: `pip install streamlit`
2. Execute manualmente: `streamlit run agent/ui/dashboard.py`
3. Verifique se porta 8501 está disponível

## 📚 Referências

- [VRM Specification](https://vrm.dev/en/)
- [Live2D Cubism](https://www.live2d.com/en/)
- [EdgeTTS Documentation](https://github.com/rany2/edge-tts)
- [Vosk Speech Recognition](https://alphacephei.com/vosk/)
- [Streamlit Documentation](https://docs.streamlit.io/)

## 🔮 Futuras Melhorias

- [ ] Suporte a múltiplos avatares simultâneos
- [ ] Integração com Unity/Unreal Engine para renderização avançada
- [ ] Expressões faciais baseadas em análise de sentimento do texto
- [ ] Gestos corporais e movimentos de mãos
- [ ] Cenários/fundos personalizáveis
- [ ] Streaming para OBS/vMix
- [ ] Suporte a WebRTC para interface web

## 📄 Licença

Este módulo faz parte do projeto Autonomous Agent. Consulte o LICENSE principal.
