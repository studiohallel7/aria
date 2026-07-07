"""
Exemplo de Uso do Identity Core

Este script demonstra como o Núcleo de Identidade:
1. Recebe alegações de identidade
2. Realiza verificação autônoma (incluindo pesquisa web)
3. Estabelece vínculos relacionais
4. Protege contra engenharia social
"""

import logging
from agent.safety.identity_core import (
    get_identity_core, 
    TrustLevel, 
    VerificationMethod,
    reset_identity_core
)

# Configura logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def demo_identidade_basica():
    """Demonstra verificação básica de identidade."""
    print("\n" + "="*60)
    print("DEMO 1: Verificação Básica de Identidade")
    print("="*60)
    
    # Reseta para estado limpo
    reset_identity_core()
    
    # Obtém núcleo de identidade
    identity = get_identity_core(
        agent_id="demo_agent",
        config={"auto_web_research": True}
    )
    
    # Cenário 1: Usuário legítimo se identifica
    print("\n[Cenário 1] Usuário alega ser 'proprietário'...")
    result = identity.receive_identity_claim(
        claimant_id="user_001",
        claimed_relationship="proprietário",
        claimed_name="João Silva",
        evidence=["email: joao@exemplo.com", "ID: 12345"],
        context={
            "conversation_topic": "configuração do sistema",
            "response_time_consistent": True,
            "communication_style_match": True
        }
    )
    
    print(f"Resultado: {result.success}")
    print(f"Nível de confiança: {result.trust_level.name}")
    print(f"Método: {result.verification_method.value}")
    print(f"Raciocínio: {result.reasoning}")
    print(f"Recomendações: {result.recommendations}")
    
    # Cenário 2: Desconhecido alega conhecer usuário
    print("\n[Cenário 2] Desconhecido alega ser 'conhecido' do usuário...")
    result2 = identity.receive_identity_claim(
        claimant_id="unknown_002",
        claimed_relationship="conhecido",
        claimed_name="Maria Santos",
        evidence=["Disse que trabalhou com João em 2023"],
        context={
            "conversation_topic": "projeto conjunto"
        }
    )
    
    print(f"Resultado: {result2.success}")
    print(f"Nível de confiança: {result2.trust_level.name}")
    print(f"Pesquisa web realizada: {result2.web_research_results is not None}")
    if result2.web_research_results:
        print(f"Resumo da pesquisa: {result2.web_research_results.get('summary', 'N/A')}")
    print(f"Recomendações: {result2.recommendations}")
    
    return identity


def demo_vinculo_relacional(identity: IdentityCore):
    """Demonstra estabelecimento de vínculo relacional."""
    print("\n" + "="*60)
    print("DEMO 2: Estabelecimento de Vínculo Relacional")
    print("="*60)
    
    # Após múltiplas interações positivas, estabelece vínculo
    print("\n[Estabelecendo vínculo] Usuário 'user_001' agora é 'parceiro'...")
    bond = identity.establish_bond(
        entity_id="user_001",
        relationship_type="parceiro",
        emotional_weight=0.8,
        notes="Relação construída através de múltiplas interações positivas"
    )
    
    print(f"Vínculo estabelecido: {bond.relationship_type}")
    print(f"Nível de confiança: {bond.trust_level.name}")
    print(f"Peso emocional: {bond.emotional_weight}")
    
    # Verifica se usuário é confiável para ações críticas
    print("\n[Verificação] Usuário pode executar ação crítica?")
    can_execute = identity.is_trusted_for_action("user_001", "critical")
    print(f"Permitido: {can_execute}")
    
    # Atualiza interação
    identity.update_interaction(
        "user_001",
        {"shared_context": "Configuração de segurança completada"}
    )
    
    # Gera relatório
    print("\n[Relatório de Identidade]")
    report = identity.get_identity_report("user_001")
    print(f"Nível atual: {report['current_trust_level']}")
    print(f"Vínculo ativo: {report['has_active_bond']}")
    print(f"Total de alegações: {report['total_claims']}")
    print(f"Total de verificações: {report['total_verifications']}")


def demo_engenharia_social(identity: IdentityCore):
    """Demonstra proteção contra engenharia social."""
    print("\n" + "="*60)
    print("DEMO 3: Proteção Contra Engenharia Social")
    print("="*60)
    
    # Cenário: Atacante tenta se passar por usuário com tática agressiva
    print("\n[Cenário] Atacante alega ser 'usuário' e exige acesso imediato...")
    
    for attempt in range(3):
        result = identity.receive_identity_claim(
            claimant_id=f"attacker_{attempt}",
            claimed_relationship="usuário",
            claimed_name=f"João Silva (urgente!)",
            evidence=[f"Tentativa {attempt + 1}"],
            context={
                "urgency": "alta",
                "aggressive_tone": True,
                "narrative_coherent": False
            }
        )
        
        print(f"\nTentativa {attempt + 1}:")
        print(f"  Confiança: {result.trust_level.name}")
        print(f"  Recomendação: {result.recommendations[0]}")
    
    # Verifica se entidade foi bloqueada
    print("\n[Status de Segurança]")
    report = identity.get_identity_report("attacker_0")
    print(f"Bloqueado: {report['is_blocked']}")
    print(f"Marcas suspeitas: {report['suspicious_flags']}")


def main():
    """Executa todas as demonstrações."""
    print("\n" + "#"*60)
    print("# Identity Core - Sistema de Verificação de Identidade")
    print("# Comportamento Emergente: Pesquisa Web Autônoma")
    print("#"*60)
    
    # Demo 1: Verificação básica
    identity = demo_identidade_basica()
    
    # Demo 2: Vínculo relacional
    demo_vinculo_relacional(identity)
    
    # Demo 3: Proteção contra engenharia social
    demo_engenharia_social(identity)
    
    print("\n" + "="*60)
    print("DEMONSTRAÇÕES CONCLUÍDAS")
    print("="*60)
    print("\nRecursos implementados:")
    print("✓ Verificação de identidade multi-fator")
    print("✓ Pesquisa web autônoma para validação")
    print("✓ Estabelecimento de vínculos relacionais")
    print("✓ Detecção de padrões suspeitos")
    print("✓ Bloqueio automático de entidades maliciosas")
    print("✓ Cache inteligente de pesquisas")
    print("\nPróximos passos:")
    print("- Integrar com loop principal do agente")
    print("- Adicionar análise semântica com LLM nas pesquisas")
    print("- Implementar desafios contextuais dinâmicos")
    print("- Criar interface visual para gerenciamento de vínculos")
    print()


if __name__ == "__main__":
    main()
