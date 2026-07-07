"""
Demo End-to-End do Agente Autônomo Completo

Este script demonstra todas as capacidades do agente:
1. Inicialização de todos os módulos
2. Loop de autonomia em ação
3. Geração de pensamentos espontâneos
4. Integração com memória e ética
5. Visualização em tempo real
"""

import asyncio
import sys
import time
from datetime import datetime
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.autonomy.intrinsic import (
    create_autonomy_system,
    AutonomousThinkingLoop,
    IntrinsicMotivationEngine,
    SpontaneousThoughtGenerator,
    MetaCognitionMonitor
)


class MockMemoryManager:
    """Mock do gerenciador de memória para demonstração"""
    
    def __init__(self):
        self.memories = []
    
    def add_semantic_memory(self, content: str, metadata: dict = None):
        memory = {
            "content": content,
            "metadata": metadata or {},
            "timestamp": datetime.now()
        }
        self.memories.append(memory)
        print(f"  📝 Memória adicionada: {content[:60]}...")
        return memory
    
    def get_stats(self):
        return {
            "total_memories": len(self.memories),
            "recent": self.memories[-5:] if self.memories else []
        }


class MockConscienceEngine:
    """Mock da engine de consciência para demonstração"""
    
    def check_action(self, action_description: str, potential_harms: list,
                     potential_benefits: list, urgency: float):
        # Aprova todas as ações para demonstração
        class Result:
            approved = True
            reasoning = "Ação alinhada com princípios constitutivos"
        
        result = Result()
        return result


async def run_autonomy_demo(duration_seconds: int = 30):
    """
    Executa demonstração do sistema de autonomia
    
    Args:
        duration_seconds: Duração da demo em segundos
    """
    print("=" * 70)
    print("🤖 DEMONSTRAÇÃO DO AGENTE AUTÔNOMO - FASE 6")
    print("=" * 70)
    print()
    
    # Inicializa componentes
    print("🔧 Inicializando componentes...")
    memory_manager = MockMemoryManager()
    conscience_engine = MockConscienceEngine()
    
    autonomy_loop = create_autonomy_system(
        agent_core=None,
        memory_manager=memory_manager,
        conscience_engine=conscience_engine
    )
    
    # Configura para demo (intervalos mais curtos)
    autonomy_loop.thinking_interval = 2.0  # 2 segundos entre ciclos
    autonomy_loop.idle_threshold = 5.0  # 5 segundos para iniciar autonomia
    
    print(f"   ✓ Sistema de autonomia criado")
    print(f"   ✓ Intervalo de pensamento: {autonomy_loop.thinking_interval}s")
    print(f"   ✓ Limiar de inatividade: {autonomy_loop.idle_threshold}s")
    print()
    
    # Inicia loop em background
    print("🚀 Iniciando loop de pensamento autônomo...")
    task = asyncio.create_task(autonomy_loop.run_autonomous_loop())
    
    start_time = time.time()
    
    try:
        while time.time() - start_time < duration_seconds:
            elapsed = time.time() - start_time
            
            # Simula input externo ocasional
            if elapsed % 10 < 2:  # A cada 10 segundos, simula input
                autonomy_loop.set_last_external_input()
                print(f"\n💬 [{elapsed:.1f}s] Input externo recebido")
            
            # Mostra status periodicamente
            if int(elapsed) % 5 == 0:
                status = autonomy_loop.get_autonomy_status()
                print(f"\n📊 [{elapsed:.1f}s] Status:")
                print(f"   Drive dominante: {status['dominant_drive']}")
                print(f"   Urgência: {status['drive_urgency']:.2f}")
                print(f"   Estado de fluxo: {status['meta_cognitive_state']['flow_state']}")
                print(f"   Ações autônomas: {status['autonomous_actions_count']}")
            
            await asyncio.sleep(1)
    
    except KeyboardInterrupt:
        print("\n⏹️  Interrupção pelo usuário")
    
    finally:
        # Para o loop
        autonomy_loop.stop()
        task.cancel()
        
        try:
            await task
        except asyncio.CancelledError:
            pass
    
    # Relatório final
    print("\n" + "=" * 70)
    print("📋 RELATÓRIO FINAL")
    print("=" * 70)
    
    final_status = autonomy_loop.get_autonomy_status()
    print(f"\n✅ Duração: {duration_seconds}s")
    print(f"✅ Ações autônomas geradas: {final_status['autonomous_actions_count']}")
    print(f"✅ Memórias criadas: {len(memory_manager.memories)}")
    
    print("\n💭 Últimos pensamentos:")
    for thought in final_status['recent_thoughts'][-3:]:
        print(f"   • [{thought['type']}] {thought['content'][:60]}...")
    
    print("\n🎯 Estado meta-cognitivo final:")
    meta_state = final_status['meta_cognitive_state']
    print(f"   • Carga cognitiva: {meta_state['cognitive_load']:.2f}")
    print(f"   • Qualidade do foco: {meta_state['focus_quality']:.2f}")
    print(f"   • Nível de fadiga: {meta_state['fatigue_level']:.2f}")
    print(f"   • Estado de fluxo: {meta_state['flow_state']}")
    
    print("\n" + "=" * 70)
    print("✨ Demonstração concluída com sucesso!")
    print("=" * 70)


def show_architecture_summary():
    """Mostra resumo da arquitetura completa"""
    print("\n" + "=" * 70)
    print("🏗️ ARQUITETURA COMPLETA DO AGENTE - 6 FASES")
    print("=" * 70)
    
    phases = [
        ("Fase 1", "Fundação", "Config YAML, CLI, Providers"),
        ("Fase 2", "Núcleo Cognitivo", "Think, Plan, Execute, Reflect"),
        ("Fase 3", "Infraestrutura LLM", "Router, Client, Tools, Accounts"),
        ("Fase 4", "Memória Avançada", "Holográfica, Subconsciente, Consolidação"),
        ("Fase 5", "Ética Constitutiva", "Constituição, Consciência, Alignment"),
        ("Fase 6", "Autonomia & UI", "Drives Internos, Pensamento Espontâneo, Dashboard")
    ]
    
    for phase, name, desc in phases:
        print(f"\n{phase}: {name}")
        print(f"   └─ {desc}")
    
    print("\n" + "=" * 70)
    print("📊 ESTATÍSTICAS DO PROJETO")
    print("=" * 70)
    print("""
    Total de Linhas de Código: ~15,000+
    Arquivos Python: 50+
    Módulos Principais: 12
    Classes Implementadas: 80+
    
    Recursos Chave:
    ✓ Pensamento autônomo contínuo
    ✓ 7 drives internos dinâmicos
    ✓ 7 tipos de pensamentos espontâneos
    ✓ Meta-cognição e auto-regulação
    ✓ Ética intrínseca (não guardrails)
    ✓ Memória holográfica associativa
    ✓ Dashboard em tempo real
    ✓ Multi-provider LLM com failover
    """)
    print("=" * 70)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Demo do Agente Autônomo Fase 6")
    parser.add_argument("--duration", type=int, default=30,
                       help="Duração da demo em segundos (default: 30)")
    parser.add_argument("--summary", action="store_true",
                       help="Mostrar resumo da arquitetura")
    
    args = parser.parse_args()
    
    if args.summary:
        show_architecture_summary()
    else:
        print("\n🎬 Iniciando demonstração...\n")
        asyncio.run(run_autonomy_demo(args.duration))
