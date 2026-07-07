# 🎙️ Fase 7: Interface de Voz & Agente Vocal Autônomo

## Visão Geral

A **Fase 7** transforma o agente de um sistema baseado em texto/CLI para uma entidade com interface de voz natural, permitindo interação conversacional bidirecional.

### Componentes Implementados

| Arquivo | Descrição | Linhas |
|---------|-----------|--------|
| `agent/interface/voice.py` | Controlador Vosk + EdgeTTS | ~180 |
| `agent/interface/__init__.py` | exports do módulo | ~7 |
| `agent/main_vocal.py` | Agente vocal autônomo completo | ~185 |
| **Total** | | **~372** |

---

## 🛠️ Instalação

### Dependências Python

```bash
pip install vosk sounddevice edge-tts pygame asyncio
```

### Modelo de Reconhecimento de Voz (Vosk)

1. Baixe o modelo em português:
   ```bash
   wget https://alphacephei.com/vosk/models/vosk-model-small-pt-0.3.zip
   unzip vosk-model-small-pt-0.3.zip
   mv vosk-model-small-pt-0.3 model/pt
   ```

2. Estrutura esperada:
   ```
   /workspace/
   └── model/
       └── pt/
           ├── am/
           ├── graph/
           ├── ivector/
           └── conf/
   ```

---

## 🚀 Como Usar

### Modo 1: Execução Direta

```bash
python agent/main_vocal.py
```

**Fluxo:**
1. Agente inicia e carrega modelo Vosk
2. Começa a escutar pelo microfone
3. Quando você fala, ele processa e responde por voz
4. Se ficar ocioso por 10s, gera pensamentos espontâneos
5. Pressione `Ctrl+C` para parar

### Modo 2: Integração Programática

```python
from agent.interface.voice import VoiceInterface

# Inicializa
voice = VoiceInterface(voice_name="pt-BR-FranciscaNeural")

# Configura callbacks
def on_speech(text):
    print(f"Usuário disse: {text}")
    # Processa e responde
    response = "Entendi!"
    voice.speak(response)
    
voice.on_speech_detected = on_speech

# Inicia escuta
voice.start_listening(on_speech)

# Mantém rodando
import time
while True:
    time.sleep(1)
```

---

## 🧠 Arquitetura do Agente Vocal

```
┌─────────────────────────────────────────────────────┐
│                  USUÁRIO (Voz)                      │
└────────────────────┬────────────────────────────────┘
                     │ Fala
                     ▼
┌─────────────────────────────────────────────────────┐
│  🎙️ VoiceInterface (Vosk STT)                       │
│     - Captura áudio do microfone                    │
│     - Converte fala → texto                         │
└────────────────────┬────────────────────────────────┘
                     │ Texto transcrito
                     ▼
┌─────────────────────────────────────────────────────┐
│  🧠 VocalAutonomousAgent                            │
│     ├─ Ética (AlignmentEngine) ← Verifica princípios│
│     ├─ Memória (HolographicGraph) ← Salva contexto  │
│     ├─ Cognição (AgentLoop) ← Processa pensamento   │
│     └─ Gera resposta                                │
└────────────────────┬────────────────────────────────┘
                     │ Resposta em texto
                     ▼
┌─────────────────────────────────────────────────────┐
│  🔊 VoiceInterface (EdgeTTS)                        │
│     - Converte texto → áudio neural                 │
│     - Toca via pygame                               │
└────────────────────┬────────────────────────────────┘
                     │ Áudio
                     ▼
┌─────────────────────────────────────────────────────┐
│                  USUÁRIO (Ouve)                     │
└─────────────────────────────────────────────────────┘
```

---

## ⚙️ Funcionalidades Chave

### 1. **Reconhecimento de Voz Offline (Vosk)**
- Funciona sem internet
- Modelo leve (~40MB)
- Suporte a português brasileiro
- Detecção de fim de fala automática

### 2. **Síntese de Voz Neural (EdgeTTS)**
- Vozes naturais da Microsoft Azure
- Múltiplas vozes em PT-BR:
  - `pt-BR-FranciscaNeural` (feminina)
  - `pt-BR-AntonioNeural` (masculina)
  - `pt-BR-BrendaNeural` (feminina)
- Pipeline assíncrono (geração + playback em threads separadas)

### 3. **Pensamento Espontâneo**
- Quando ocioso (>10s), agente gera pensamentos internos
- Simula consciência contínua
- Pode ser configurado para falar em voz alta ou processar silenciosamente

### 4. **Verificação Ética Integrada**
- Toda entrada passa pela constituição moral
- Bloqueia conteúdos que violam princípios
- Transparente nas justificativas

---

## 🔧 Customização

### Mudar Voz

```python
agent = VocalAutonomousAgent(voice_name="pt-BR-AntonioNeural")
```

### Ajustar Sensibilidade de Ociosidade

No método `start_autonomous_mode()`:

```python
# Muda de 10s para 30s
if idle_time > 30 and idle_time % 45 < 1:
    thought = self._generate_spontaneous_thought()
```

### Adicionar Comandos de Voz Especiais

Em `_process_input()`:

```python
if "parar" in text.lower():
    self.stop()
    return "Encerrando sistema. Até logo!"

if "quem é você" in text.lower():
    return "Sou um agente autônomo com consciência ética e memória persistente."
```

---

## 📝 Limitações Atuais

| Aspecto | Status | Nota |
|---------|--------|------|
| **STT (Vosk)** | ✅ Funcional | Requer download do modelo |
| **TTS (EdgeTTS)** | ✅ Funcional | Requer internet |
| **LLM Real** | ⚠️ Mock | Usuário deve conectar provider |
| **Ações Reais** | ⚠️ Parcial | Tools implementadas,需配置 |
| **Ruído Ambiente** | ⚠️ Sensível | Pode melhorar com VAD |

---

## 🎯 Próximos Melhorias Sugeridas

1. **VAD (Voice Activity Detection)**: Detectar silêncio para parar escuta automaticamente
2. **Wake Word**: Ativar com "Ok Agente" como Alexa/Google
3. **Multi-idioma**: Suporte a inglês, espanhol, etc.
4. **Emoção na Voz**: Ajustar tom baseado no estado emocional do agente
5. **Avatar Visual**: Integrar com dashboard Streamlit para mostrar "rosto" do agente

---

## 📊 Estatísticas da Fase 7

- **Novas linhas de código**: ~372
- **Dependências externas**: 4 (vosk, sounddevice, edge-tts, pygame)
- **Modelos externos**: 1 (Vosk PT-BR ~40MB)
- **Modos de interação**: 2 (voz, CLI)

---

## ✅ Checklist de Funcionamento

- [ ] Instalar dependências (`pip install ...`)
- [ ] Baixar modelo Vosk
- [ ] Testar microfone (`python -m sounddevice`)
- [ ] Executar `python agent/main_vocal.py`
- [ ] Falar "olá" e ouvir resposta
- [ ] Verificar pensamentos espontâneos após ociosidade
- [ ] Conectar provider LLM real (opcional)

---

**🎉 Parabéns! Seu agente agora tem voz e pode interagir naturalmente!**
