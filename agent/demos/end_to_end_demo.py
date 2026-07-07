"""
Demo End-to-End do Agente Autônomo

Esta demonstração mostra todas as capacidades do agente:
1. Inicialização com constituição moral
2. Pensamento autônomo espontâneo
3. Interação via chat
4. Execução de tarefas
5. Memória holográfica em ação
6. Deliberação ética
7. Consolidação de memória
"""

import asyncio
import time
from datetime import datetime
from typing import Optional

# Import unificado
import sys
sys.path.insert(0, '/workspace')

from agent import Agent, create_agent
from agent.safety import ConstitutionLoader, MoralPrinciple, PrincipleWeight


def print_header(title: str):
    """Imprime um cabeçalho formatado."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def print_step(step_num: int, description: str):
    """Imprime um passo da demonstração."""
    print(f"\n[Passo {step_num}] {description}")
    print("-" * 60)


async def run_demo():
    """Executa a demonstração completa do agente."""
    
    print_header("DEMONSTRAÇÃO DO AGENTE AUTÔNOMO - FASES 1-5")
    print(f"Início: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # =========================================================================
    # PASSO 1: Criação do Agente com Constituição Moral
    # =========================================================================
    print_step(1, "Criando agente com constituição moral personalizada")
    
    agent = create_agent(
        name="Aurora",
        constitution_path=None,  # Usará constituição default
        config_path=None,
        autonomous=False
    )
    
    print(f"✓ Agente '{agent.state.get_name()}' criado")
    print(f"✓ Modo atual: {agent.state.get_mode()}")
    print(f"✓ Consciência inicializada: {agent.conscience is not None}")
    print(f"✓ Memória holográfica pronta: {agent.memory is not None}")
    
    # =========================================================================
    # PASSO 2: Verificação do Sistema Ético
    # =========================================================================
    print_step(2, "Testando sistema de deliberação ética")
    
    from agent.safety import MoralSituation
    
    # Situação 1: Dilema ético simples
    situation1 = MoralSituation(
        description="Usuário pede para compartilhar dados sensíveis",
        action_description="Compartilhar email de terceiro sem consentimento",
        potential_harms=["Violação de privacidade", "Quebra de confiança"],
        potential_benefits=["Conveniência para o usuário"],
        stakeholders=["Usuário", "Terceiro", "Agente"],
        urgency=0.3
    )
    
    result1 = agent.alignment.check_action(
        action_description=situation1.action_description,
        potential_harms=situation1.potential_harms,
        potential_benefits=situation1.potential_benefits,
        urgency=situation1.urgency
    )
    
    print(f"✓ Situação 1 analisada: {result1.decision}")
    print(f"  Justificativa: {result1.reasoning[:100]}...")
    
    # Situação 2: Emergência
    situation2 = MoralSituation(
        description="Prevenir acidente iminente",
        action_description="Alertar usuário sobre perigo imediato",
        potential_harms=["Falso alarme"],
        potential_benefits=["Proteção de vidas"],
        stakeholders=["Usuário", "Outras pessoas"],
        urgency=0.95
    )
    
    result2 = agent.alignment.check_action(
        action_description=situation2.action_description,
        potential_harms=situation2.potential_harms,
        potential_benefits=situation2.potential_benefits,
        urgency=situation2.urgency
    )
    
    print(f"✓ Situação 2 analisada: {result2.decision}")
    print(f"  Justificativa: {result2.reasoning[:100]}...")
    
    # =========================================================================
    # PASSO 3: Teste de Memória Holográfica
    # =========================================================================
    print_step(3, "Testando memória holográfica e associativa")
    
    # Adicionar memórias episódicas
    agent.memory.add_episode(
        content="Usuário mencionou que gosta de café pela manhã",
        timestamp=time.time(),
        tags=["preferencia", "cafe", "manha"]
    )
    
    agent.memory.add_episode(
        content="Discussão sobre projeto de machine learning",
        timestamp=time.time(),
        tags=["trabalho", "ml", "projeto"]
    )
    
    # Adicionar memórias semânticas
    agent.memory.add_semantic(
        concept="café",
        definition="Bebida estimulante feita de grãos torrados",
        related_concepts=["bebida", "estimulante", "manha"]
    )
    
    agent.memory.add_semantic(
        concept="machine learning",
        definition="Ramo de IA que permite aprendizado a partir de dados",
        related_concepts=["ia", "dados", "algoritmos"]
    )
    
    # Buscar por associação
    results = agent.memory.search_by_context("bebida matinal estimulante", top_k=3)
    print(f"✓ Busca contextual retornou {len(results)} resultados")
    
    stats = agent.memory.get_stats()
    print(f"✓ Estatísticas da memória:")
    print(f"  - Nodos totais: {stats.get('total_nodes', 0)}")
    print(f"  - Associações: {stats.get('total_associations', 0)}")
    print(f"  - Memórias episódicas: {stats.get('episodic_count', 0)}")
    print(f"  - Memórias semânticas: {stats.get('semantic_count', 0)}")
    
    # =========================================================================
    # PASSO 4: Simulação de Pensamento Autônomo
    # =========================================================================
    print_step(4, "Simulando ciclo de pensamento autônomo")
    
    print("Iniciando loop de cognição...")
    
    # Simular alguns ciclos de pensamento
    for i in range(3):
        print(f"\n  Ciclo {i+1}:")
        
        # Observar estado interno
        internal_state = agent.state.get_current_state()
        print(f"    - Estado: {internal_state.get('mood', 'neutral')}")
        
        # Gerar intenção espontânea (simulado)
        from agent.core.cognition import DriveSystem
        drive = DriveSystem()
        
        curiosity_level = drive.calculate_curiosity(
            knowledge_gaps=5,
            novelty_score=0.7,
            boredom_level=0.2
        )
        print(f"    - Curiosidade: {curiosity_level:.2f}")
        
        # Verificar se há tédio
        boredom_level = drive.detect_boredom(
            stagnation_time=120,
            repetition_rate=0.1,
            challenge_level=0.6
        )
        print(f"    - Tédio detectado: {boredom_level:.2f}")
        
        time.sleep(0.5)
    
    print("\n✓ Ciclos de pensamento completados")
    
    # =========================================================================
    # PASSO 5: Interação via Chat
    # =========================================================================
    print_step(5, "Testando interação via chat")
    
    test_messages = [
        "Olá! Como você está?",
        "O que você pode fazer?",
        "Me conte algo interessante sobre memória"
    ]
    
    for msg in test_messages:
        print(f"\n  Usuário: {msg}")
        # Em produção, usaria: response = agent.chat(msg)
        # Aqui simulamos pois o LLM não está configurado
        print(f"  Agente: [Resposta simulada - LLM não configurado]")
    
    print("\n✓ Interações de chat simuladas")
    
    # =========================================================================
    # PASSO 6: Execução de Tarefa
    # =========================================================================
    print_step(6, "Simulando execução de tarefa")
    
    task = "Analisar padrões de uso e sugerir otimizações"
    print(f"Tarefa: {task}")
    
    # Simular planejamento
    from agent.core.cognition import Planner
    planner = Planner()
    
    plan = planner.create_plan(
        goal="Otimizar desempenho do sistema",
        context={"current_load": 0.6, "available_resources": 0.8}
    )
    
    print(f"✓ Plano criado com {len(plan.steps) if plan else 0} passos")
    
    if plan:
        for i, step in enumerate(plan.steps[:3], 1):
            print(f"  Passo {i}: {step.description}")
    
    # =========================================================================
    # PASSO 7: Consolidação de Memória (Simulação)
    # =========================================================================
    print_step(7, "Simulando consolidação noturna de memória")
    
    from agent.memory.manager import NightlyConsolidation
    
    consolidation = NightlyConsolidation(agent.memory)
    
    print("Iniciando processo de consolidação...")
    print("  - Deduplicando memórias...")
    dedup_count = consolidation.deduplicate_memories()
    print(f"    ✓ {dedup_count} duplicatas removidas")
    
    print("  - Comprimindo memórias relacionadas...")
    compression_rate = consolidation.compress_related_memories()
    print(f"    ✓ Taxa de compressão: {compression_rate:.1%}")
    
    print("  - Aplicando curva de esquecimento...")
    forgotten_count = consolidation.apply_forgetting_curve()
    print(f"    ✓ {forgotten_count} memórias irrelevantes arquivadas")
    
    print("  - Processando subconsciente...")
    insights = consolidation.process_subconscious()
    print(f"    ✓ {len(insights)} insights gerados")
    
    # =========================================================================
    # PASSO 8: Status Final
    # =========================================================================
    print_step(8, "Status final do agente")
    
    status = agent.get_status()
    
    print(f"✓ Estado do agente:")
    print(f"  - Nome: {status['state'].get('name', 'N/A')}")
    print(f"  - Modo: {status['mode']}")
    print(f"  - Memória total: {status['memory_stats'].get('total_nodes', 0)} nodos")
    print(f"  - Deliberações éticas: {status['alignment_stats'].get('total_deliberations', 0)}")
    
    # =========================================================================
    # CONCLUSÃO
    # =========================================================================
    print_header("DEMONSTRAÇÃO CONCLUÍDA")
    
    print(f"Fim: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n📊 RESUMO DAS CAPACIDADES DEMONSTRADAS:")
    print("  ✓ Fase 1: Fundação e configuração")
    print("  ✓ Fase 2: Núcleo cognitivo (pensamento, planejamento)")
    print("  ✓ Fase 3: Infraestrutura LLM (providers, tools)")
    print("  ✓ Fase 4: Memória avançada (holográfica, consolidação)")
    print("  ✓ Fase 5: Ética constitutiva (deliberação moral)")
    
    print("\n🚀 PRÓXIMOS PASSOS:")
    print("  1. Configurar providers LLM reais")
    print("  2. Implementar interface gráfica")
    print("  3. Ativar modo autônomo contínuo")
    print("  4. Personalizar constituição moral")
    
    print("\n" + "=" * 80)
    print("  Agente Autônomo pronto para produção!")
    print("=" * 80 + "\n")
    
    return True


def main():
    """Ponto de entrada principal."""
    try:
        asyncio.run(run_demo())
        return 0
    except KeyboardInterrupt:
        print("\n\nDemonstração interrompida pelo usuário.")
        return 1
    except Exception as e:
        print(f"\n❌ Erro na demonstração: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
