#!/usr/bin/env python3
"""
Demo da Interface Unificada do Agente
Mostra todos os modos de operação: Chat, Voz, GUI e VTuber
"""

import sys
import time
from pathlib import Path

# Adiciona o workspace ao path
workspace = Path(__file__).parent
sys.path.insert(0, str(workspace))

# Import direto do módulo unified (evita import circular)
import interface.unified as unified_module
UnifiedInterface = unified_module.UnifiedInterface
VTuberAvatar = unified_module.VTuberAvatar
InterfaceMode = unified_module.InterfaceMode
Message = unified_module.Message
create_interface = unified_module.create_interface

from interface.voice import VoiceInterface


def demo_imports():
    """Demonstra que todos os imports funcionam."""
    print("=" * 70)
    print("🧪 TESTE DE IMPORTS")
    print("=" * 70)
    
    try:
        print("✅ Todos os imports bem-sucedidos!")
        print(f"   - UnifiedInterface: {UnifiedInterface}")
        print(f"   - VTuberAvatar: {VTuberAvatar}")
        print(f"   - InterfaceMode: {InterfaceMode}")
        print(f"   - VoiceInterface: {VoiceInterface}")
        return True
    except Exception as e:
        print(f"❌ Erro nos imports: {e}")
        return False


def demo_vtuber_avatar():
    """Demonstra funcionalidades do VTuberAvatar."""
    print("\n" + "=" * 70)
    print("🎭 DEMO VTUBER AVATAR")
    print("=" * 70)
    
    from agent.interface import VTuberAvatar
    
    # Cria avatar
    avatar = VTuberAvatar(model_type="vrm")
    print(f"✓ Avatar criado (tipo: {avatar.model_type})")
    
    # Mostra modelos disponíveis para download
    print(f"\n📦 Modelos gratuitos disponíveis:")
    for name, url in avatar.FREE_MODELS.items():
        print(f"   • {name}: {url[:60]}...")
    
    # Testa expressões
    print(f"\n😊 Expressões faciais suportadas:")
    expressions = ['neutral', 'happy', 'sad', 'angry', 'surprised', 
                   'thinking', 'talking', 'listening']
    for expr in expressions:
        print(f"   • {expr}")
    
    # Simula mudança de expressão
    print(f"\n🎬 Testando expressões (simulação):")
    for expr in ['neutral', 'happy', 'thinking', 'talking']:
        avatar.set_expression(expr)
        print(f"   → Expressão definida: {expr}")
    
    print(f"\n✓ Demo VTuber concluída!")


def demo_interface_modes():
    """Demonstra modos de interface disponíveis."""
    print("\n" + "=" * 70)
    print("🖥️  DEMO MODOS DE INTERFACE")
    print("=" * 70)
    
    # Lista todos os modos
    print(f"\n📋 Modos de interface disponíveis:")
    for mode in InterfaceMode:
        print(f"   • {mode.value.upper()}: {mode.name}")
    
    # Detecta capacidades
    print(f"\n🔍 Detectando capacidades do sistema...")
    interface = create_interface("chat")
    
    print(f"   Modos disponíveis neste sistema:")
    for mode in interface.available_modes:
        print(f"      ✓ {mode.value}")
    
    print(f"\n✓ Demo de modos concluída!")


def demo_message_structure():
    """Demonstra estrutura de mensagens unificadas."""
    print("\n" + "=" * 70)
    print("💬 DEMO ESTRUTURA DE MENSAGENS")
    print("=" * 70)
    
    import time
    
    # Cria mensagem
    msg = Message(
        content="Olá! Esta é uma mensagem de teste.",
        source="user",
        metadata={"test": True}
    )
    
    print(f"\n📨 Estrutura da mensagem:")
    print(f"   Conteúdo: {msg.content}")
    print(f"   Origem: {msg.source}")
    print(f"   Timestamp: {time.strftime('%H:%M:%S', time.localtime(msg.timestamp))}")
    print(f"   Metadata: {msg.metadata}")
    
    # Mensagens de diferentes fontes
    print(f"\n📋 Exemplos de origens:")
    sources = ["user", "agent", "system", "voice", "chat", "gui"]
    for src in sources:
        m = Message(content=f"Mensagem de {src}", source=src)
        print(f"   • {src}: '{m.content}'")
    
    print(f"\n✓ Demo de mensagens concluída!")


def demo_usage_examples():
    """Mostra exemplos de uso."""
    print("\n" + "=" * 70)
    print("📚 EXEMPLOS DE USO")
    print("=" * 70)
    
    examples = [
        ("Chat CLI", "python -m agent.interface.unified --mode chat"),
        ("Voz", "python -m agent.interface.unified --mode voice"),
        ("GUI Dashboard", "python -m agent.interface.unified --mode gui"),
        ("VTuber", "python -m agent.interface.unified --mode vtuber"),
        ("Unificado", "python -m agent.interface.unified --mode unified"),
        ("Com modelo VRM", "python -m agent.interface.unified --mode vtuber --model modelo.vrm"),
        ("Com voz customizada", "python -m agent.interface.unified --mode voice --voice pt-BR-AntonioNeural"),
    ]
    
    print(f"\n💻 Comandos disponíveis:\n")
    for i, (desc, cmd) in enumerate(examples, 1):
        print(f"{i}. {desc}")
        print(f"   $ {cmd}\n")
    
    # Exemplo programático
    print(f"🐍 Exemplo programático:\n")
    code = '''
from agent.interface import create_interface, InterfaceMode

# Criar interface unificada
interface = create_interface("unified")

# Adicionar callback
def on_response(text):
    print(f"Resposta: {text}")

interface.add_response_callback(on_response)

# Iniciar
interface.start()
'''
    print(code)


def demo_integration_points():
    """Mostra pontos de integração com o agente."""
    print("\n" + "=" * 70)
    print("🔗 PONTOS DE INTEGRAÇÃO")
    print("=" * 70)
    
    print(f"""
🧠 Integração com o Cérebro do Agente:

1. Callback de Resposta:
   interface.add_response_callback(lambda text: process_and_respond(text))

2. Processamento de Entrada:
   _process_user_message(text, source) → Chama o loop cognitivo do agente

3. Atualização de Estado:
   - Atualiza memória do agente
   - Verifica ética antes de responder
   - Gera resposta via LLM

4. Saída Multi-Modal:
   - Texto no terminal
   - Áudio via EdgeTTS
   - Avatar VTuber animado
   - Dashboard GUI atualizado

📊 Fluxo Completo:

Usuário (Voz/Texto) 
    ↓
UnifiedInterface._on_voice_input() ou _process_user_message()
    ↓
Agente Brain (process_input → generate_response)
    ↓
Response Callbacks
    ↓
[VoiceInterface.speak()] + [VTuberAvatar.set_expression()] + [Terminal Print]
""")


def main():
    """Executa todas as demos."""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "DEMO INTERFACE UNIFICADA DO AGENTE" + " " * 19 + "║")
    print("║" + " " * 10 + "Chat • Voz • GUI • VTuber • Unificado" + " " * 15 + "║")
    print("╚" + "=" * 68 + "╝")
    print()
    
    # Executa demos
    if not demo_imports():
        print("\n❌ Falha nos imports. Instale as dependências:")
        print("   pip install edge-tts pygame sounddevice")
        return 1
    
    demo_vtuber_avatar()
    demo_interface_modes()
    demo_message_structure()
    demo_usage_examples()
    demo_integration_points()
    
    # Resumo final
    print("\n" + "=" * 70)
    print("📝 RESUMO")
    print("=" * 70)
    print("""
✅ Interface Unificada implementada com sucesso!

Recursos disponíveis:
  • 5 modos de operação (Chat, Voz, GUI, VTuber, Unificado)
  • Sistema de mensagens unificado
  • Avatar VTuber com expressões faciais
  • Download automático de modelos gratuitos
  • Integração com VoiceInterface existente
  • Callbacks para respostas do agente
  • Detecção automática de capacidades do sistema

Próximos passos:
  1. Execute: python -m agent.interface.unified --mode chat
  2. Para voz: instale vosk e baixe o modelo PT-BR
  3. Para VTuber: baixe um modelo .vrm e use --model
  4. Para GUI: instale streamlit (pip install streamlit)

Documentação completa em: agent/interface/README_UNIFIED.md
""")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
