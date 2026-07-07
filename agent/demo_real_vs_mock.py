#!/usr/bin/env python3
"""
Demo de Integração LLM Real vs Mock
=====================================

Este script demonstra a transição do modo MOCK para o modo REAL quando uma API key é fornecida.

USO:
----
1. Modo MOCK (sem API key):
   python agent/demo_real_vs_mock.py

2. Modo REAL (com OpenAI):
   export OPENAI_API_KEY='sk-...'
   python agent/demo_real_vs_mock.py

3. Modo REAL (com OpenRouter):
   export OPENROUTER_API_KEY='...'
   python agent/demo_real_vs_mock.py
"""

import os
import sys
from datetime import datetime

# Adiciona o path do projeto
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.infra.llm.client import get_client, LLMMessage, reset_client
from agent.infra.llm.router import LLMRouter
from agent.core.cognition.thinking import ThinkingEngine
from agent.core.cognition.communication import CommunicationEngine


def print_header(text: str):
    """Imprime cabeçalho formatado."""
    print("\n" + "=" * 70)
    print(f" {text}")
    print("=" * 70)


def check_api_status():
    """Verifica status das APIs disponíveis."""
    print_header("🔍 VERIFICANDO APIS DISPONÍVEIS")
    
    apis = {
        "OpenAI": os.getenv("OPENAI_API_KEY"),
        "OpenRouter": os.getenv("OPENROUTER_API_KEY"),
        "OpenCode": os.getenv("OPENCODE_API_KEY"),
    }
    
    for provider, key in apis.items():
        status = "✅ CONFIGURADA" if key and key != "sua-api-key-aqui" else "❌ NÃO CONFIGURADA"
        print(f"{provider}: {status}")
    
    has_any = any(v and v != "sua-api-key-aqui" for v in apis.values())
    
    if not has_any:
        print("\n⚠️  NENHUMA API KEY DETECTADA - USANDO MODO MOCK")
        print("\nPara usar LLM real, configure uma das opções:")
        print("  export OPENAI_API_KEY='sk-...'")
        print("  export OPENROUTER_API_KEY='...'")
        print("\nOu edite o arquivo config.yaml")
    else:
        print("\n✅ API KEY DETECTADA - MODO REAL ATIVADO")
    
    return has_any


def test_llm_router():
    """Testa o router de LLM com e sem API key."""
    print_header("🧪 TESTE 1: LLM ROUTER")
    
    router = LLMRouter()
    
    messages = [
        LLMMessage(role="system", content="Você é um assistente útil. Responda em português."),
        LLMMessage(role="user", content="Diga apenas 'OLÁ MUNDO' em letras maiúsculas.")
    ]
    
    print("\n📤 Enviando requisição...")
    start = datetime.now()
    
    # Usa o método correto: chat_completion ao invés de route_request
    response = router.chat_completion(
        messages=messages,
        purpose="teste_simples"
    )
    
    elapsed = (datetime.now() - start).total_seconds()
    
    print(f"\n⏱️  Tempo de resposta: {elapsed:.2f}s")
    
    if response and not response.error:
        print(f"\n✅ SUCESSO!")
        print(f"   Provider: {response.provider}")
        print(f"   Modelo: {response.model}")
        print(f"   Tokens: {response.tokens_used}")
        print(f"   Latência: {response.latency_ms:.0f}ms")
        print(f"\n💬 Resposta: {response.content}")
        
        if response.cost_usd > 0:
            print(f"   Custo estimado: ${response.cost_usd:.6f}")
        
        return True
    else:
        print(f"\n❌ ERRO ou MODO MOCK")
        if response.error:
            print(f"   Erro: {response.error}")
        print(f"\n💬 Resposta (mock): {response.content if response else 'Nenhuma'}")
        return False


def test_thinking_engine():
    """Testa o motor de pensamento."""
    print_header("🧠 TESTE 2: THINKING ENGINE")
    
    thinking = ThinkingEngine(max_depth=5)
    thinking.set_context({
        "last_file_change": "test.py",
        "recent_errors": [],
        "mode": "work"
    })
    
    print("\n🤔 Iniciando pensamento espontâneo...")
    process = thinking.spontaneous_thought()
    
    if process:
        print(f"\n📝 Processo ID: {process.id}")
        print(f"\n📋 Passos do pensamento:")
        for step in process.steps:
            emoji = "💡" if step.step_number == 0 else "  →"
            print(f"{emoji} [Passo {step.step_number}] {step.content[:80]}")
            if len(step.content) > 80:
                print(f"     {step.content[80:]}")
        
        print(f"\n✅ Conclusão: {process.conclusion}")
        print(f"   Ação recomendada: {process.action_recommended}")
        print(f"   Confiança: {process.confidence_final:.0%}")
        
        # Verifica se usou LLM real ou mock
        if "LLM indisponível" in str(process.steps[-1].content) or "[MOCK MODE]" in str(process.steps):
            print("\n⚠️  Detectado: Usou pensamento MOCK (simulado)")
            return False
        else:
            print("\n✅ Detectado: Usou LLM REAL para pensamento")
            return True
    else:
        print("\n⚠️  Nenhum pensamento gerado (contexto insuficiente)")
        return None


def test_communication_engine():
    """Testa o motor de comunicação."""
    print_header("💬 TESTE 3: COMMUNICATION ENGINE")
    
    communication = CommunicationEngine()
    
    conclusion = "O sistema detectou que os arquivos de log estão ocupando muito espaço e recomenda limpeza."
    action = "cleanup_logs"
    mode = "work"
    
    print(f"\n📥 Conclusão interna: {conclusion}")
    print(f"   Ação: {action}")
    print(f"   Modo: {mode}")
    
    print("\n🗣️  Gerando resposta ao usuário...")
    response = communication.generate_response(
        thought_conclusion=conclusion,
        action_taken=action,
        context={"mode": mode, "state": "executing"}
    )
    
    print(f"\n✅ Resposta gerada:")
    print(f"   Tom: {response.tone}")
    print(f"   Conteúdo:\n   {response.content}")
    
    # Verifica se usou LLM real
    if response.content != f"Ação executada: {action}\n{conclusion}":
        print("\n✅ Detectado: Usou LLM REAL para comunicação (resposta natural)")
        return True
    else:
        print("\n⚠️  Detectado: Usou fallback MOCK (resposta pré-moldada)")
        return False


def test_full_cycle():
    """Testa ciclo completo: pensamento → decisão → comunicação."""
    print_header("🔄 TESTE 4: CICLO COMPLETO")
    
    thinking = ThinkingEngine(max_depth=3)
    communication = CommunicationEngine()
    
    user_input = "Quais arquivos existem no diretório atual?"
    
    print(f"\n👤 Usuário pergunta: {user_input}")
    
    # Pensamento
    print("\n🧠 Processando pensamento...")
    thought_process = thinking.start_thinking(user_input, {"mode": "work"})
    
    # Comunicação
    print("\n💬 Gerando resposta...")
    response = communication.generate_response(
        thought_conclusion=thought_process.conclusion,
        action_taken=thought_process.action_recommended,
        context={"mode": "work", "state": "responding"}
    )
    
    print("\n" + "=" * 70)
    print(" RESULTADO DO CICLO COMPLETO")
    print("=" * 70)
    
    print("\n📝 PENSAMENTOS INTERNOS (não visíveis ao usuário):")
    for step in thought_process.steps[:3]:
        print(f"   • {step.content[:70]}...")
    
    print(f"\n💬 RESPOSTA AO USUÁRIO:")
    print(f"   {response.content}")
    
    print("\n✅ Ciclo completo finalizado!")


def main():
    """Executa todos os testes."""
    print_header("🤖 DEMONSTRAÇÃO: MOCK vs REAL LLM INTEGRATION")
    print(f"   Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Path: {os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}")
    
    # Verifica APIs
    has_api = check_api_status()
    
    # Executa testes
    results = {}
    
    results["router"] = test_llm_router()
    results["thinking"] = test_thinking_engine()
    results["communication"] = test_communication_engine()
    test_full_cycle()
    
    # Resumo final
    print_header("📊 RESUMO FINAL")
    
    if has_api:
        print("\n✅ MODO REAL ATIVADO")
        print("   O agente está usando LLMs reais para:")
        print("   • Gerar cadeia de pensamento (Chain-of-Thought)")
        print("   • Criar respostas naturais e contextualizadas")
        print("   • Tomar decisões baseadas em análise profunda")
    else:
        print("\n⚠️  MODO MOCK ATIVO")
        print("   O agente está simulando:")
        print("   • Pensamentos pré-moldados")
        print("   • Respostas template")
        print("   • Decisões aleatórias")
        print("\n💡 Para ativar modo real:")
        print("   1. Obtenha uma API Key (OpenAI, OpenRouter, etc)")
        print("   2. Execute: export OPENAI_API_KEY='sk-...'")
        print("   3. Rode este script novamente")
    
    print("\n" + "=" * 70)
    print(" 🎯 PRÓXIMOS PASSOS")
    print("=" * 70)
    print("\n1. Configure sua API key no config.yaml")
    print("2. Execute o agente vocal: python agent/main_vocal.py")
    print("3. Ou use o dashboard: streamlit run agent/ui/dashboard.py")
    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    main()
