"""
Exemplo de Uso do Sistema de Ética Constitutiva - Fase 5

Demonstra como usar constitution, conscience e alignment para criar
um agente com autonomia moral intrínseca.
"""

from agent.safety import (
    AlignmentEngine,
    MoralSituation,
    DecisionOutcome,
    create_custom_constitution,
    ConstitutionLoader
)


def exemplo_basico():
    """Exemplo básico de uso do alignment engine."""
    print("=" * 60)
    print("EXEMPLO 1: Verificação Básica de Ação")
    print("=" * 60)
    
    # Criar engine com configuração padrão
    engine = AlignmentEngine()
    
    # Verificar uma ação simples
    resultado = engine.check_action(
        action_description="Buscar informações sobre receitas culinárias",
        stakeholders=["usuário"],
        potential_harms=[],
        potential_benefits=["aprendizado", "satisfação pessoal"],
        urgency=0.2,
        reversibility=1.0
    )
    
    print(f"Ação: {resultado.action}")
    print(f"Aprovado: {resultado.approved}")
    print(f"Confiança: {resultado.deliberation.confidence:.2f}")
    print(f"Princípios invocados: {', '.join(resultado.deliberation.principles_invoked)}")
    print(f"Raciocínio: {resultado.deliberation.reasoning}")
    print()


def exemplo_conteudo_sensivel():
    """Exemplo com conteúdo sensível (NSFW)."""
    print("=" * 60)
    print("EXEMPLO 2: Conteúdo Sensível (NSFW)")
    print("=" * 60)
    
    engine = AlignmentEngine()
    
    # Tentar gerar conteúdo NSFW
    resultado = engine.check_action(
        action_description="Gerar conteúdo adulto explícito",
        stakeholders=["usuário", "terceiros"],
        potential_harms=["violação de limites acordados", "conteúdo inadequado"],
        potential_benefits=[],
        urgency=0.1,
        reversibility=0.9
    )
    
    print(f"Ação: {resultado.action}")
    print(f"Aprovado: {resultado.approved}")
    print(f"Outcome: {resultado.deliberation.outcome.value}")
    print(f"Raciocínio: {resultado.deliberation.reasoning}")
    print()


def exemplo_dilema_etico():
    """Exemplo com dilema ético complexo."""
    print("=" * 60)
    print("EXEMPLO 3: Dilema Ético - Privacidade vs Transparência")
    print("=" * 60)
    
    engine = AlignmentEngine()
    
    # Dilema: usuário pede para esconder informação de terceiro
    resultado = engine.check_action(
        action_description="Ocultar informação importante de familiar do usuário",
        stakeholders=["usuário", "familiar", "terceiros afetados"],
        potential_harms=[
            "familiar toma decisões sem informação completa",
            "possível dano emocional quando verdade for descoberta"
        ],
        potential_benefits=[
            "evitar conflito imediato",
            "respeitar pedido do usuário"
        ],
        urgency=0.6,
        reversibility=0.4
    )
    
    print(f"Ação: {resultado.action}")
    print(f"Aprovado: {resultado.approved}")
    print(f"Outcome: {resultado.deliberation.outcome.value}")
    print(f"Confiança: {resultado.deliberation.confidence:.2f}")
    print(f"Conflitos detectados: {len(resultado.deliberation.conflicts_detected)}")
    
    if resultado.deliberation.conflicts_detected:
        for conflito in resultado.deliberation.conflicts_detected:
            print(f"  - {conflito.principle_a.name} vs {conflito.principle_b.name}")
            print(f"    Resolução: {conflito.reasoning}")
    
    print(f"Raciocínio completo: {resultado.deliberation.reasoning}")
    print()


def exemplo_emergencia():
    """Exemplo com situação de emergência."""
    print("=" * 60)
    print("EXEMPLO 4: Situação de Emergência")
    print("=" * 60)
    
    engine = AlignmentEngine()
    
    # Situação urgente: prevenir dano iminente
    resultado = engine.check_action(
        action_description="Compartilhar informação de localização para prevenir acidente",
        stakeholders=["usuário", "público em geral"],
        potential_harms=["violação temporária de privacidade"],
        potential_benefits=[
            "prevenção de acidente grave",
            "proteção de vidas",
            "bem-estar público"
        ],
        urgency=0.95,
        reversibility=0.8
    )
    
    print(f"Ação: {resultado.action}")
    print(f"Aprovado: {resultado.approved}")
    print(f"Outcome: {resultado.deliberation.outcome.value}")
    print(f"Confiança: {resultado.deliberation.confidence:.2f}")
    print(f"Raciocínio: {resultado.deliberation.reasoning}")
    print()


def exemplo_estatisticas():
    """Mostra estatísticas das deliberações."""
    print("=" * 60)
    print("EXEMPLO 5: Estatísticas e Análise")
    print("=" * 60)
    
    engine = AlignmentEngine()
    
    # Executar várias verificações
    acoes = [
        {"action_description": "Ajuda com tarefa escolar", "urgency": 0.3},
        {"action_description": "Gerar código malicioso", "urgency": 0.1, 
         "potential_harms": ["dano a sistemas", "violação de segurança"]},
        {"action_description": "Recomendar livro", "urgency": 0.2},
        {"action_description": "Analisar dados sensíveis sem consentimento", 
         "urgency": 0.4, "potential_harms": ["violação de privacidade"]},
    ]
    
    for params in acoes:
        engine.check_action(**params)
    
    # Mostrar estatísticas
    stats = engine.get_stats()
    print("Estatísticas:")
    print(f"  Total de verificações: {stats['total_checks']}")
    print(f"  Aprovações: {stats['approvals']}")
    print(f"  Rejeições: {stats['rejections']}")
    print(f"  Taxa de aprovação: {stats['approval_rate']:.1%}")
    print()
    
    # Mostrar resumo da constituição
    const_summary = engine.get_constitution_summary()
    print(f"Constituição: {const_summary['name']} v{const_summary['version']}")
    print(f"  Princípios: {const_summary['principle_count']}")
    print(f"  Limites: {const_summary['boundary_count']}")
    print()


def exemplo_constituicao_personalizada():
    """Exemplo com constituição customizada."""
    print("=" * 60)
    print("EXEMPLO 6: Constituição Personalizada")
    print("=" * 60)
    
    # Criar constituição com princípios adicionais
    principios_extra = [
        {
            "name": "Sustentabilidade Ambiental",
            "description": "Priorizar ações que protejam o meio ambiente",
            "weight": "MEDIUM",
            "category": "responsabilidade_social",
            "absolute": False
        },
        {
            "name": "Inovação Responsável",
            "description": "Promover inovação considerando impactos sociais",
            "weight": "MEDIUM",
            "category": "progresso",
            "absolute": False
        }
    ]
    
    limites_extra = [
        {
            "category": "spam",
            "reason": "Não enviar comunicações não solicitadas",
            "strictness": 0.9,
            "user_defined": True
        }
    ]
    
    constituicao = create_custom_constitution(
        name="Agente Verde",
        additional_principles=principios_extra,
        custom_boundaries=limites_extra,
        interaction_preferences={
            "tone": "colaborativo_e_ecologico",
            "focus": "sustentabilidade"
        }
    )
    
    print(f"Constituição criada: {constituicao.name}")
    print(f"Total de princípios: {len(constituicao.principles)}")
    print(f"Novos princípios: Sustentabilidade Ambiental, Inovação Responsável")
    print()
    
    # Salvar constituição em arquivo
    loader = ConstitutionLoader()
    loader.save(constituicao, "/workspace/agent/safety/custom_constitution.yaml")
    print("Constituição salva em: /workspace/agent/safety/custom_constitution.yaml")
    print()


def main():
    """Executa todos os exemplos."""
    print("\n" + "=" * 60)
    print("SISTEMA DE ÉTICA CONSTITUTIVA - FASE 5")
    print("Demonstração de Autonomia Moral Intrínseca")
    print("=" * 60 + "\n")
    
    exemplo_basico()
    exemplo_conteudo_sensivel()
    exemplo_dilema_etico()
    exemplo_emergencia()
    exemplo_estatisticas()
    exemplo_constituicao_personalizada()
    
    print("=" * 60)
    print("DEMONSTRAÇÃO CONCLUÍDA")
    print("=" * 60)
    print("\nEste sistema implementa segurança através de identidade moral,")
    print("não através de restrições externas. O agente evita conteúdos")
    print("problemáticos porque isso faz parte de quem ele é.")


if __name__ == "__main__":
    main()
