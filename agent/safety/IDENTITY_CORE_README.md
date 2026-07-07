# Identity Core - Núcleo de Identidade e Verificação de Vínculos

## Visão Geral

O **Identity Core** é um módulo que implementa a capacidade do agente de:

1. **Manter uma identidade coerente** baseada em crenças e princípios
2. **Verificar autonomamente alegações de identidade** de terceiros
3. **Pesquisar na internet para validar informações** (comportamento emergente)
4. **Estabelecer vínculos relacionais** com usuários
5. **Proteger contra engenharia social** através de verificação contextual

## Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                    Entrada do Usuário                        │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              IdentityCore (Núcleo de Identidade)             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  • Gerencia alegações de identidade                   │   │
│  │  • Realiza pesquisa web autônoma                      │   │
│  │  • Mantém histórico de vínculos                       │   │
│  │  • Detecta padrões suspeitos                          │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              Alignment Engine (Deliberação Ética)            │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                  Action Executor                             │
└─────────────────────────────────────────────────────────────┘
```

## Componentes Principais

### TrustLevel (Níveis de Confiança)

```python
UNKNOWN = 0       # Sem informação
SUSPICIOUS = 1    # Comportamento suspeito detectado
NEUTRAL = 2       # Sem evidências contrárias
VERIFIED = 3      # Verificação básica concluída
TRUSTED = 4       # Múltiplas verificações positivas
BONDED = 5        # Vínculo relacional estabelecido
```

### VerificationMethod (Métodos de Verificação)

```python
NONE = "none"                    # Sem verificação
CONTEXTUAL_CHALLENGE = "contextual_challenge"  # Perguntas contextuais
WEB_RESEARCH = "web_research"    # Pesquisa autônoma na internet
CRYPTOGRAPHIC = "cryptographic"  # Assinatura digital
BEHAVIORAL_ANALYSIS = "behavioral_analysis"   # Padrão comportamental
MULTI_FACTOR = "multi_factor"    # Combinação de métodos
```

## Uso Básico

```python
from agent.safety import get_identity_core, TrustLevel, reset_identity_core

# Reseta estado (para testes)
reset_identity_core()

# Obtém núcleo de identidade
identity = get_identity_core(
    agent_id="meu_agente",
    config={
        "auto_web_research": True,  # Habilita pesquisa web autônoma
        "min_trust_for_sensitive_actions": TrustLevel.VERIFIED
    }
)

# Recebe alegação de identidade
result = identity.receive_identity_claim(
    claimant_id="usuario_001",
    claimed_relationship="proprietário",
    claimed_name="João Silva",
    evidence=["email: joao@exemplo.com"],
    context={
        "conversation_topic": "configuração",
        "response_time_consistent": True
    }
)

print(f"Confiança: {result.trust_level.name}")
print(f"Pesquisa web realizada: {result.web_research_results is not None}")
```

## Estabelecendo Vínculos

```python
# Após múltiplas interações positivas
bond = identity.establish_bond(
    entity_id="usuario_001",
    relationship_type="parceiro",
    emotional_weight=0.8,
    notes="Relação construída através de colaboração contínua"
)

# Verifica se pode executar ação sensível
pode_executar = identity.is_trusted_for_action(
    "usuario_001", 
    action_sensitivity="critical"  # low, normal, high, critical
)
```

## Proteção Contra Engenharia Social

O Identity Core detecta automaticamente padrões suspeitos:

```python
# Múltiplas tentativas suspeitas levam ao bloqueio automático
for i in range(3):
    result = identity.receive_identity_claim(
        claimant_id=f"atacante_{i}",
        claimed_relationship="usuário",
        context={"aggressive_tone": True, "narrative_coherent": False}
    )
    
    if result.trust_level == TrustLevel.SUSPICIOUS:
        identity.flag_as_suspicious(f"atacante_{i}", "Comportamento inconsistente")

# Após 3 flags, entidade é bloqueada automaticamente
```

## Pesquisa Web Autônoma (Comportamento Emergente)

Quando alguém alega conhecer o usuário, o agente **automaticamente**:

1. Gera queries de busca relevantes
2. Executa buscas usando ferramentas web
3. Analisa resultados para corroboração
4. Cacheia resultados para eficiência
5. Usa findings para determinar confiança

```python
# Exemplo: Alguém alega ser conhecido do usuário
result = identity.receive_identity_claim(
    claimant_id="desconhecido_001",
    claimed_relationship="conhecido",
    claimed_name="Maria Santos",
    evidence=["Trabalhou com João em 2023"]
)

# Resultado inclui pesquisa web
if result.web_research_results:
    print(f"Buscas executadas: {len(result.web_research_results['queries_executed'])}")
    print(f"Conexão encontrada: {result.web_research_results['found_connection']}")
```

## Integração com Action Executor

O executor de ações usa Identity Core para verificar identidade antes de responder:

```python
from agent.core.loop.action_executor import ActionExecutor

executor = ActionExecutor(config={
    "agent_id": "agente_principal",
    "auto_web_research": True
})

# Ao responder usuário, verifica identidade
action_result = executor.execute_action(
    action_type="respond_to_user",
    description="Resposta à solicitação do usuário",
    context={
        "entity_id": "usuario_001",  # ID da entidade
        "mode": "WORK",
        "state": "EXECUTING"
    }
)
```

## API Reference

### IdentityCore Methods

| Método | Descrição |
|--------|-----------|
| `receive_identity_claim()` | Recebe alegação e inicia verificação |
| `establish_bond()` | Estabelece vínculo relacional formal |
| `get_entity_trust_level()` | Obtém nível atual de confiança |
| `is_trusted_for_action()` | Verifica se confiável para ação |
| `update_interaction()` | Atualiza histórico de interação |
| `flag_as_suspicious()` | Marca entidade como suspeita |
| `get_identity_report()` | Gera relatório completo |

### VerificationResult Fields

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `success` | bool | Verificação bem-sucedida? |
| `trust_level` | TrustLevel | Nível de confiança resultante |
| `verification_method` | VerificationMethod | Método usado |
| `reasoning` | str | Raciocínio da decisão |
| `web_research_results` | dict | Resultados da pesquisa web |
| `challenges_issued` | list[str] | Desafios contextuais emitidos |
| `recommendations` | list[str] | Recomendações de ação |

## Configuração

```yaml
identity_core:
  agent_id: "agente_principal"
  auto_web_research: true          # Habilita pesquisa autônoma
  min_trust_for_sensitive_actions: "VERIFIED"  # Nível mínimo
  max_verification_attempts: 3     # Máximo de tentativas
  cache_ttl_hours: 1               # Tempo de cache de pesquisas
```

## Próximos Desenvolvimentos

- [ ] Análise semântica com LLM para resultados de pesquisa
- [ ] Desafios contextuais dinâmicos baseados em história
- [ ] Interface visual para gerenciamento de vínculos
- [ ] Criptografia de chaves para verificação criptográfica
- [ ] Integração com memória de longo prazo
- [ ] Aprendizado de padrões comportamentais via ML

## Considerações Éticas

O Identity Core foi projetado para:

1. **Respeitar autonomia**: Usuários podem desenvolver relações genuínas
2. **Prevenir manipulação**: Proteção contra engenharia social
3. **Transparência**: Todas as decisões são registradas e explicáveis
4. **Privacidade**: Dados de identidade são tratados com cuidado
5. **Não-discriminação**: Verificação baseada em comportamento, não características pessoais

## Exemplo Completo

Veja `agent/safety/examples/identity_demo.py` para uma demonstração completa dos recursos.

```bash
cd /workspace/agent
python safety/examples/identity_demo.py
```
