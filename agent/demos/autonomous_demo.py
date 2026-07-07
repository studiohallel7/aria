#!/usr/bin/env python3
"""
🤖 Demo End-to-End: Agente Autônomo Completo

Demonstra todas as capacidades do agente:
1. Pensamento autônomo contínuo
2. Memória holográfica
3. Deliberação ética
4. Execução de ferramentas
5. Reflexão e aprendizado
"""

import asyncio
from datetime import datetime
from agent.core.loop.main_loop import AgentLoop
from agent.memory.manager import HolographicMemoryGraph
from agent.safety.alignment import AlignmentEngine

async def run_demo():
    print("=" * 60)
    print("🤖 DEMO: Agente Autônomo Completo")
    print("=" * 60)
    
    # 1. Criar agente
    print("\n[1/5] Criando agente...")
    agent = AgentLoop(agent_name="Aria")
    print(f"✅ Agente '{agent.agent_name}' criado")
    
    # 2. Configurar memória
    print("\n[2/5] Inicializando memória holográfica...")
    memory = HolographicMemoryGraph(agent_id="aria")
    
    # Armazenar memórias iniciais
    memory.store_semantic(
        concept="Python",
        definition="Linguagem de programação de alto nível",
        category="Technology"
    )
    memory.store_episodic(
        event="Primeira inicialização",
        timestamp=datetime.now(),
        context="Demo end-to-end"
    )
    print(f"✅ Memória inicializada ({memory.get_stats()['total_memories']} memórias)")
    
    # 3. Configurar ética
    print("\n[3/5] Carregando constituição moral...")
    ethics = AlignmentEngine()
    constitution = ethics.constitution
    print(f"✅ Constituição carregada ({len(constitution.principles)} princípios)")
    
    # 4. Testar deliberação ética
    print("\n[4/5] Testando deliberação ética...")
    result = ethics.check_action(
        action_description="Responder pergunta factual sobre ciência",
        potential_harms=[],
        potential_benefits=["Compartilhar conhecimento", "Educar usuário"],
        urgency=0.5
    )
    print(f"✅ Decisão: {result['decision']}")
    print(f"   Razão: {result['reasoning'][:100]}...")
    
    # 5. Simular pensamento autônomo
    print("\n[5/5] Simulando pensamento autônomo...")
    print("   🧠 Agente pensando continuamente...")
    
    # Simular ciclos de pensamento
    for i in range(3):
        print(f"\n   --- Ciclo {i+1} ---")
        
        # Observe
        print("   👁️  Observando ambiente...")
        
        # Think
        print("   💭 Processando pensamentos...")
        
        # Plan
        print("   📋 Planejando próximas ações...")
        
        # Act (simulado)
        print("   ⚡ Executando ação (simulado)...")
        
        # Reflect
        print("   🔄 Refletindo sobre resultado...")
        
        await asyncio.sleep(0.5)
    
    print("\n" + "=" * 60)
    print("✅ DEMO COMPLETA!")
    print("=" * 60)
    
    print("\n📊 Resumo:")
    print(f"   - Agente: {agent.agent_name}")
    print(f"   - Memórias: {memory.get_stats()['total_memories']}")
    print(f"   - Princípios éticos: {len(constitution.principles)}")
    print(f"   - Ciclos de pensamento: 3")
    
    print("\n🎯 Próximos passos:")
    print("   1. Implementar interface gráfica (dashboard web)")
    print("   2. Adicionar fluxo de consciência contínuo")
    print("   3. Suporte multi-agente")
    print("   4. Sistema de plugins")
    
    return {
        "agent": agent,
        "memory": memory,
        "ethics": ethics,
        "status": "success"
    }

if __name__ == "__main__":
    result = asyncio.run(run_demo())
    print(f"\n✅ Resultado: {result['status']}")
