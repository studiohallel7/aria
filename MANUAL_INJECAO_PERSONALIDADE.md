# Manual de Injeção de Personalidade do Agente Cognitivo

## Visão Geral

Este manual descreve como configurar e personalizar a personalidade do agente cognitivo através dos módulos de **DriveSystem**, **BoredomEngine**, e outros componentes cognitivos. A personalidade do agente é definida pela combinação de perfis motivacionais, thresholds de comportamento e configurações dos sistemas internos.

---

## 1. Arquitetura de Personalidade

A personalidade do agente é composta por 5 módulos principais que devem estar integrados ao loop principal:

### 1.1 Módulos Cognitivos

| Módulo | Arquivo | Função | Status |
|--------|---------|--------|--------|
| **DriveSystem** | `core/cognition/drive.py` | Gerencia 7 drives motivacionais | ✅ Integrado |
| **BoredomEngine** | `core/cognition/boredom.py` | Calcula tédio, frustração e curiosidade | ✅ Integrado |
| **InternalCritic** | `core/cognition/critic.py` | Valida planos antes da execução | ✅ Integrado |
| **ContinuousInterpreter** | `core/cognition/interpretation.py` | Interpreta dados em múltiplas camadas | ✅ Integrado |
| **WorkingMemorySet** | `core/cognition/working_set.py` | Memória de trabalho para rascunho mental | ✅ Integrado |
| **ResilienceModule** | `core/autonomy/resilience.py` | Gerencia falhas e recuperação | ✅ Integrado |

---

## 2. Sistema de Drives (DriveSystem)

### 2.1 Tipos de Drives

O sistema possui 7 drives motivacionais que definem a personalidade:

```python
class DriveType(Enum):
    CURIOSITY = "curiosity"      # Vontade de explorar/descobrir
    ORDER = "order"              # Necessidade de organização
    EFFICIENCY = "efficiency"    # Otimização de recursos/processos
    PURPOSE = "purpose"          # Senso de dever/utilidade
    LEARNING = "learning"        # Desejo de aprender/evoluir
    SOCIAL = "social"            # Necessidade de interação/comunicação
    COMPLETION = "completion"    # Impulso de completar tarefas
```

### 2.2 Perfis de Personalidade Predefinidos

Os seguintes perfis estão disponíveis em `drive.py`:

#### Perfil "balanced" (Padrão)
- Equilibrado entre todos os drives
- Ideal para uso geral
- Configuração recomendada para maioria dos casos

```python
"balanced": {
    DriveType.CURIOSITY: {"weight": 1.0, "target": 50},
    DriveType.ORDER: {"weight": 1.0, "target": 60},
    DriveType.EFFICIENCY: {"weight": 1.0, "target": 70},
    DriveType.PURPOSE: {"weight": 1.2, "target": 80},
    DriveType.LEARNING: {"weight": 1.0, "target": 60},
    DriveType.SOCIAL: {"weight": 0.8, "target": 40},
    DriveType.COMPLETION: {"weight": 1.3, "target": 90}
}
```

#### Perfil "explorer"
- Alta curiosidade e desejo de aprendizado
- Menor preocupação com organização
- Ideal para agentes de pesquisa e descoberta

```python
"explorer": {
    DriveType.CURIOSITY: {"weight": 1.8, "target": 70},
    DriveType.ORDER: {"weight": 0.6, "target": 40},
    DriveType.EFFICIENCY: {"weight": 0.8, "target": 50},
    DriveType.PURPOSE: {"weight": 1.0, "target": 60},
    DriveType.LEARNING: {"weight": 1.6, "target": 80},
    DriveType.SOCIAL: {"weight": 0.7, "target": 30},
    DriveType.COMPLETION: {"weight": 0.9, "target": 70}
}
```

#### Perfil "worker"
- Foco em eficiência, ordem e completude
- Alto senso de propósito
- Ideal para agentes de produção e automação

```python
"worker": {
    DriveType.CURIOSITY: {"weight": 0.7, "target": 40},
    DriveType.ORDER: {"weight": 1.4, "target": 80},
    DriveType.EFFICIENCY: {"weight": 1.6, "target": 90},
    DriveType.PURPOSE: {"weight": 1.8, "target": 95},
    DriveType.LEARNING: {"weight": 0.9, "target": 60},
    DriveType.SOCIAL: {"weight": 0.5, "target": 30},
    DriveType.COMPLETION: {"weight": 1.8, "target": 95}
}
```

#### Perfil "scholar"
- Ênfase máxima em aprendizado e curiosidade
- Moderado em organização
- Ideal para agentes de análise e estudo

```python
"scholar": {
    DriveType.CURIOSITY: {"weight": 1.5, "target": 70},
    DriveType.ORDER: {"weight": 1.2, "target": 70},
    DriveType.EFFICIENCY: {"weight": 1.0, "target": 60},
    DriveType.PURPOSE: {"weight": 1.1, "target": 70},
    DriveType.LEARNING: {"weight": 1.9, "target": 90},
    DriveType.SOCIAL: {"weight": 0.6, "target": 30},
    DriveType.COMPLETION: {"weight": 1.2, "target": 80}
}
```

### 2.3 Como Configurar o Perfil

No arquivo `main_loop.py` ou via configuração:

```python
config = {
    "personality_profile": "explorer",  # balanced, worker, scholar, explorer
    "max_working_items": 20,
    "working_set_ttl": 600,
    # ... outras configurações
}

agent = AgentLoop(config=config)
```

---

## 3. Sistema de Tédio (BoredomEngine)

### 3.1 Níveis de Tédio

```python
class BoredomLevel(Enum):
    ENGAGED = "engaged"       # 0-20%: Totalmente engajado
    CONTENT = "content"       # 20-40%: Satisfeito
    RESTLESS = "restless"     # 40-60%: Inquieto
    BORED = "bored"           # 60-80%: Entediado
    DESPERATE = "desperate"   # 80-100%: Desesperado por estímulo
```

### 3.2 Ações Autônomas por Tédio

| Nível | Ações Sugeridas | Comportamento |
|-------|-----------------|---------------|
| ENGAGED | WAIT | Aguarda comandos |
| CONTENT | WAIT, REFLECT | Reflexões ocasionais |
| RESTLESS | EXPLORE, LEARN, REFLECT | Busca ativa por estímulos |
| BORED | ASK_USER, CLEANUP, OPTIMIZE | Pede tarefas, organiza |
| DESPERATE | ASK_USER, EXPLORE | Insiste por interação |

### 3.3 Thresholds Configuráveis

Em `boredom.py`, ajuste os thresholds para comportamento autônomo:

```python
self.boredom_thresholds = {
    "explore": 45.0,      # Score mínimo para explorar
    "learn": 55.0,        # Score mínimo para aprender
    "reflect": 65.0,      # Score mínimo para refletir
    "cleanup": 70.0,      # Score mínimo para organizar
    "ask_user": 80.0,     # Score mínimo para pedir tarefa
    "desperate_action": 90.0  # Score para ações desesperadas
}
```

### 3.4 Taxas de Decaimento

```python
self.idle_decay_rate = 0.5      # Pontos de tédio por segundo ocioso
self.frustration_rate = 0.1     # Acúmulo de frustração sem propósito
self.curiosity_recovery = 0.3   # Recuperação de curiosidade ao agir
```

---

## 4. Crítico Interno (InternalCritic)

### 4.1 Função

Valida planos antes da execução, identificando:
- Dependências circulares
- Recursos faltantes
- Ações críticas sem confirmação
- Timeout estimado vs limite
- Falta de plano B
- Desalinhamento com objetivo

### 4.2 Níveis de Severidade

```python
class CriticSeverity(Enum):
    LOW = "low"          # Observações menores
    MEDIUM = "medium"    # Requer atenção
    HIGH = "high"        # Pode reprovar plano
    CRITICAL = "critical" # Reprova plano automaticamente
```

### 4.3 Integração no Loop

O crítico é chamado automaticamente em `_plan()`:

```python
# Valida plano com InternalCritic
critique_report = self.critic.evaluate_plan(plan_data, context)

if not critique_report.is_approved:
    # Plano rejeitado - requer refinamento
    return False
```

---

## 5. Intérprete Contínuo (ContinuousInterpreter)

### 5.1 Camadas de Interpretação

```python
class InterpretationLayer(Enum):
    LITERAL = "literal"        # O que foi dito
    CONTEXTUAL = "contextual"  # Significado no contexto
    INTENTIONAL = "intentional" # Intenção por trás
    EMOTIONAL = "emotional"    # Estado emocional implícito
    IMPLICIT = "implicit"      # O que não foi dito
```

### 5.2 Configuração de Sensibilidade

Em `interpretation.py`:

```python
self.ambiguity_threshold = 0.3      # Acima disso, pede clarificação
self.emotional_sensitivity = 0.7    # Sensibilidade a tons emocionais
```

### 5.3 Padrões de Intenção

O intérprete detecta automaticamente:
- **Request**: "preciso", "quero", "faça", "crie"
- **Question**: "como", "por que", "quando", "onde"
- **Command**: "execute", "rode", "inicie", "pare"
- **Suggestion**: "talvez", "poderia", "que tal"
- **Frustration**: "não funciona", "erro", "falhou"
- **Urgency**: "agora", "urgente", "rápido"

---

## 6. Memória de Trabalho (WorkingMemorySet)

### 6.1 Função

Espaço temporário para:
- Testar ideias e descartá-las
- Formular e validar hipóteses
- Iterar rascunhos de planos
- Mapear restrições

### 6.2 Tipos de Itens

| Tipo | Descrição | Confiança Inicial |
|------|-----------|-------------------|
| idea | Ideias gerais | 0.5 |
| hypothesis | Hipóteses para teste | 0.3 |
| constraint | Restrições/fatos | 1.0 |
| draft | Rascunhos de plano | 0.4 |

### 6.3 Configuração

```python
config = {
    "max_working_items": 20,    # Máximo de itens na memória
    "working_set_ttl": 600      # Tempo de vida em segundos (10 min)
}
```

### 6.4 Ciclo de Vida dos Itens

1. **active** → Criado/modificado
2. **promoted** → Promovido para memória permanente (confiança ≥ 0.8)
3. **discarded** → Descartado (razão registrada)

---

## 7. Resiliência (ResilienceModule)

### 7.1 Estratégias de Recuperação

```python
class RecoveryStrategy(Enum):
    IGNORE = "ignore"              # Ignora erro
    RETRY_IMMEDIATE = "retry_immediate"    # Retry imediato
    RETRY_EXPONENTIAL = "retry_exponential" # Backoff exponencial
    FALLBACK_MODEL = "fallback_model"      # Usa modelo alternativo
    FALLBACK_MODE = "fallback_mode"        # Modo seguro
    RESTART_MODULE = "restart_module"      # Reinicia módulo
    ABORT_GRACEFULLY = "abort_gracefully"  # Aborta graciosamente
```

### 7.2 Mapeamento de Erros

```python
self.strategies = {
    "RateLimitError": RecoveryStrategy.RETRY_EXPONENTIAL,
    "ConnectionError": RecoveryStrategy.RETRY_EXPONENTIAL,
    "TimeoutError": RecoveryStrategy.RETRY_IMMEDIATE,
    "AuthenticationError": RecoveryStrategy.FALLBACK_MODEL,
    "OutOfTokensError": RecoveryStrategy.FALLBACK_MODE,
    "MemoryError": RecoveryStrategy.RESTART_MODULE,
    "PermissionError": RecoveryStrategy.ABORT_GRACEFULLY,
}
```

---

## 8. Criando um Perfil Customizado

### 8.1 Passo a Passo

#### Passo 1: Definir Novo Perfil

Crie um arquivo `agent/core/cognition/custom_profiles.py`:

```python
from agent.core.cognition.drive import DriveType

CUSTOM_PROFILES = {
    "creative_coder": {
        DriveType.CURIOSITY: {"weight": 1.6, "target": 75},
        DriveType.ORDER: {"weight": 0.8, "target": 50},
        DriveType.EFFICIENCY: {"weight": 1.2, "target": 65},
        DriveType.PURPOSE: {"weight": 1.4, "target": 80},
        DriveType.LEARNING: {"weight": 1.7, "target": 85},
        DriveType.SOCIAL: {"weight": 0.9, "target": 45},
        DriveType.COMPLETION: {"weight": 1.1, "target": 75}
    },
    
    "analyst": {
        DriveType.CURIOSITY: {"weight": 1.3, "target": 65},
        DriveType.ORDER: {"weight": 1.5, "target": 85},
        DriveType.EFFICIENCY: {"weight": 1.4, "target": 80},
        DriveType.PURPOSE: {"weight": 1.3, "target": 75},
        DriveType.LEARNING: {"weight": 1.8, "target": 90},
        DriveType.SOCIAL: {"weight": 0.4, "target": 25},
        DriveType.COMPLETION: {"weight": 1.5, "target": 85}
    }
}
```

#### Passo 2: Registrar no DriveSystem

Edite `agent/core/cognition/drive.py`:

```python
from .custom_profiles import CUSTOM_PROFILES

def _initialize_drives(self):
    profiles = {
        # ... perfis existentes ...
        **CUSTOM_PROFILES  # Adiciona perfis customizados
    }
    # ... resto do código ...
```

#### Passo 3: Usar na Configuração

```python
config = {
    "personality_profile": "creative_coder",
    # ... outras configs ...
}

agent = AgentLoop(config=config)
```

### 8.2 Exemplo de Configuração Completa

```yaml
# config/personality_config.yaml
personality:
  profile: "scholar"
  
  # Overrides específicos
  custom_weights:
    CURIOSITY: 1.8
    LEARNING: 2.0
  
  boredom_settings:
    idle_decay_rate: 0.3      # Mais lento que o padrão
    frustration_rate: 0.05    # Menos frustrável
    curiosity_recovery: 0.5   # Recupera curiosidade rápido
    
  critic_settings:
    auto_reject_critical: true
    require_fallback_plan: true
    
  working_memory:
    max_items: 25
    ttl_seconds: 900
    auto_promote_threshold: 0.75
```

---

## 9. Arquivos a Serem Modificados/Criados

### 9.1 Pelo Usuário (Configuração)

| Arquivo | Ação | Descrição |
|---------|------|-----------|
| `config/personality_config.yaml` | **Criar** | Configuração YAML da personalidade |
| `agent/core/cognition/custom_profiles.py` | **Criar** | Perfis customizados |
| `.env` | **Modificar** | Adicionar `AGENT_PERSONALITY=explorer` |

### 9.2 Pelo Agente (Automático)

| Arquivo | Ação | Descrição |
|---------|------|-----------|
| `agent/core/loop/main_loop.py` | **Ler** | Carrega configuração de personalidade |
| `agent/core/cognition/drive.py` | **Ler** | Aplica pesos e targets dos drives |
| `agent/core/cognition/boredom.py` | **Ler** | Configura thresholds de tédio |
| `agent/core/state/agent_state.py` | **Escrever** | Registra estado motivacional |
| `logs/motivation_log.json` | **Escrever** | Log de eventos motivacionais |

### 9.3 Colaborativos (Usuário + Agente)

| Arquivo | Ação Conjunta | Descrição |
|---------|---------------|-----------|
| `memory/personality_evolution.json` | **Ambos** | Histórico de evolução da personalidade |
| `config/thresholds_override.json` | **Ambos** | Overrides dinâmicos de thresholds |

---

## 10. Monitoramento e Debug

### 10.1 Comandos de Diagnóstico

```python
# Obter resumo da personalidade
summary = agent.drive_system.get_personality_summary()
print(summary)

# Obter estado de tédio
boredom_diag = agent.boredom_engine.get_diagnostics()
print(boredom_diag)

# Obter saúde do sistema
health = agent.resilience.get_health_status()
print(health)

# Obter estatísticas do crítico
critic_stats = agent.critic.get_stats()
print(critic_stats)
```

### 10.2 Logs Relevantes

Habilite logs detalhados:

```python
import logging
logging.getLogger("agent_loop").setLevel(logging.DEBUG)
logging.getLogger("drive_system").setLevel(logging.DEBUG)
logging.getLogger("boredom_engine").setLevel(logging.DEBUG)
```

### 10.3 Métricas Chave

| Métrica | Onde Ver | Valor Ideal |
|---------|----------|-------------|
| `overall_tension` | DriveSystem | 20-40 |
| `boredom_score` | BoredomEngine | 10-50 |
| `approval_rate` | InternalCritic | 0.7-0.9 |
| `health_score` | ResilienceModule | 80-100 |
| `avg_confidence` | WorkingMemorySet | 0.6-0.8 |

---

## 11. Exemplos Práticos

### 11.1 Agente Altamente Curioso

```python
config = {
    "personality_profile": "explorer",
    "max_llm_calls_per_cycle": 5,  # Mais chamadas para exploração
}

# Ajustes finos manuais
agent.boredom_engine.boredom_thresholds["explore"] = 30.0  # Explora mais cedo
agent.drive_system.drives[DriveType.CURIOSITY].priority_weight = 2.0
```

### 11.2 Agente Conservador/Cauteloso

```python
config = {
    "personality_profile": "worker",
    "auto_reject_critical": True,
    "require_high_confidence": True,
    "min_confidence_threshold": 0.85,
}

# Crítico mais rigoroso
agent.critic.ambiguity_threshold = 0.2  # Menos tolerância a ambiguidades
```

### 11.3 Agente Social/Interativo

```python
# Perfil customizado
custom_social = {
    DriveType.CURIOSITY: {"weight": 1.0, "target": 50},
    DriveType.ORDER: {"weight": 0.9, "target": 55},
    DriveType.EFFICIENCY: {"weight": 1.0, "target": 60},
    DriveType.PURPOSE: {"weight": 1.5, "target": 85},
    DriveType.LEARNING: {"weight": 1.2, "target": 65},
    DriveType.SOCIAL: {"weight": 2.0, "target": 70},  # Alto peso social
    DriveType.COMPLETION: {"weight": 1.1, "target": 75}
}

agent.drive_system.drives = custom_social
agent.boredom_engine.preferred_actions[BoredomLevel.RESTLESS].append(BoredomAction.ASK_USER)
```

---

## 12. Troubleshooting

### Problema: Agente muito passivo

**Sintoma:** Nunca toma iniciativas, sempre aguarda comandos.

**Solução:**
```python
# Aumentar decay de tédio
agent.boredom_engine.idle_decay_rate = 0.8

# Reduzir thresholds
agent.boredom_engine.boredom_thresholds["explore"] = 35.0
agent.boredom_engine.boredom_thresholds["ask_user"] = 60.0

# Aumentar peso do drive PURPOSE
agent.drive_system.drives[DriveType.PURPOSE].priority_weight = 1.8
```

### Problema: Agente muito agressivo/impulsivo

**Sintoma:** Toma muitas ações autônomas indesejadas.

**Solução:**
```python
# Reduzir decay de tédio
agent.boredom_engine.idle_decay_rate = 0.2

# Aumentar thresholds
agent.boredom_engine.boredom_thresholds["explore"] = 70.0

# Aumentar critério do crítico
agent.critic.ambiguity_threshold = 0.15
```

### Problema: Muitas falsas positivas no crítico

**Sintoma:** Planos válidos são rejeitados frequentemente.

**Solução:**
```python
# Revisar regras de validação
# Ajustar threshold de alinhamento
agent.critic.goal_alignment_threshold = 0.3  # Mais permissivo
```

---

## 13. Referências

### Arquivos Principais

```
agent/
├── core/
│   ├── cognition/
│   │   ├── drive.py              # Sistema de drives
│   │   ├── boredom.py            # Engine de tédio
│   │   ├── critic.py             # Crítico interno
│   │   ├── interpretation.py     # Intérprete contínuo
│   │   ├── working_set.py        # Memória de trabalho
│   │   └── custom_profiles.py    # [CRIAR] Perfis customizados
│   ├── autonomy/
│   │   ├── resilience.py         # Módulo de resiliência
│   │   ├── mode_manager.py       # Gerenciador de modos
│   │   └── priorities.py         # Gerenciador de prioridades
│   ├── loop/
│   │   └── main_loop.py          # Loop principal (integra tudo)
│   └── state/
│       └── agent_state.py        # Estado do agente
└── config/
    ├── personality_config.yaml   # [CRIAR] Configuração de personalidade
    └── thresholds_override.json  # [OPCIONAL] Overrides dinâmicos
```

### Documentação Relacionada

- `README.md` - Visão geral do projeto
- `docs/architecture.md` - Arquitetura do sistema
- `docs/cognitive_modules.md` - Detalhes dos módulos cognitivos

---

## 14. Checklist de Implementação

### Para Novo Perfil de Personalidade

- [ ] Definir pesos e targets para os 7 drives
- [ ] Criar entrada em `custom_profiles.py`
- [ ] Testar com `get_personality_summary()`
- [ ] Ajustar thresholds de tédio se necessário
- [ ] Validar com cenários de teste
- [ ] Documentar comportamento esperado

### Para Ajuste Fino

- [ ] Identificar métrica problemática (tédio, tensão, etc.)
- [ ] Localizar parâmetro relevante no código
- [ ] Fazer alteração incremental (±10-20%)
- [ ] Testar em ambiente controlado
- [ ] Registrar mudança em `personality_evolution.json`
- [ ] Monitorar impacto por 24-48 horas

---

**Versão do Manual:** 1.0  
**Última Atualização:** 2024  
**Compatibilidade:** Agent Loop v2.x+
