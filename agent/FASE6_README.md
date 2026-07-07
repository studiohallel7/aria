# 🤖 Agente Autônomo - Fase 6: Autonomia Profunda & Interface Gráfica

## Visão Geral

A **Fase 6** implementa a mecânica de **autonomia intrínseca** do agente, permitindo que ele pense e aja independentemente de input externo constante, além de fornecer uma interface gráfica completa para monitoramento em tempo real.

---

## 🧠 Mecânica de Autonomia

### Como o Agente Pensa Sozinho?

O sistema de autonomia é baseado em **4 pilares fundamentais**:

#### 1. **Drives Internos (Motivação Endógena)**

O agente possui 7 drives internos que geram motivação independente:

| Drive | Descrição | Comportamento Típico |
|-------|-----------|---------------------|
| `CURIOSITY` | Vontade de aprender/explorar | Faz perguntas, busca novos tópicos |
| `EFFICIENCY` | Otimizar processos | Reorganiza tarefas, simplifica fluxos |
| `CONNECTION` | Interagir com outros | Inicia conversas, verifica status |
| `CREATION` | Criar algo novo | Gera conteúdo, código, soluções |
| `ORGANIZATION` | Organizar conhecimento | Estrutura memórias, categoriza info |
| `SELF_IMPROVEMENT` | Melhorar a si mesmo | Reflete sobre desempenho |
| `REST` | Consolidação/ociosidade | Processa em background |

Cada drive tem:
- **Intensidade base**: Nível natural do drive
- **Intensidade atual**: Varia com o tempo
- **Taxa de decaimento**: Diminui se não satisfeito
- **Peso de prioridade**: Personalidade do agente
- **Urgência**: Calculada dinamicamente

#### 2. **Pensamentos Espontâneos**

O agente gera pensamentos automaticamente em 7 categorias:

```python
REFLECTION      # "Será que aquela abordagem foi a melhor?"
PLANNING        # "Preciso organizar prioridades para amanhã"
ASSOCIATION     # "Isso me lembra aquilo que aprendi antes..."
QUESTION        # "Por que isso funciona dessa maneira?"
HYPOTHESIS      # "Talvez haja um fator oculto influenciando"
CREATIVE_INSIGHT# "E se combinarmos essas ideias de forma inusitada?"
META_AWARENESS  # "Estou pensando muito, será produtivo?"
```

**Mecanismo de geração:**
1. Seleciona tipo baseado em probabilidades ponderadas
2. Gera conteúdo usando templates contextualizados
3. Cria cadeia de pensamentos relacionados
4. Decide se age sobre o pensamento (baseado na importância)
5. Registra na memória se relevante

#### 3. **Meta-Cognição**

O agente monitora seu próprio processo cognitivo:

```python
cognitive_load     # Quanto está processando (0-1)
focus_quality      # Qualidade da atenção (0-1)
processing_speed   # Velocidade relativa (0-1+)
error_rate         # Taxa estimada de erros (0-1)
learning_efficiency# Eficiência de aprendizado (0-1+)
fatigue_level      # Fadiga acumulada (0-1)
flow_state         # Está em estado de fluxo? (bool)
```

**Auto-regulação:**
- Detecta fadiga após horas de atividade
- Ajusta velocidade e precisão conforme necessário
- Entra em "estado de fluxo" quando condições são ideais
- Recomenda ajustes (descanso, redução de carga, etc.)

#### 4. **Loop de Pensamento Contínuo**

```
┌─────────────────────────────────────────┐
│  1. Verifica inatividade (>30s sem input) │
│  2. Atualiza drives internos              │
│  3. Identifica drive dominante            │
│  4. Gera pensamento espontâneo            │
│  5. Avalia eticamente (consciência)       │
│  6. Decide agir ou não                    │
│  7. Registra na memória                   │
│  8. Atualiza meta-cognição                │
│  9. Repete após intervalo (5s)            │
└─────────────────────────────────────────┘
```

---

## 🖥️ Interface Gráfica (Dashboard)

### Tecnologias Utilizadas
- **Streamlit**: Framework web Python para UI
- **Plotly**: Visualizações interativas
- **Pandas**: Manipulação de dados

### Componentes do Dashboard

#### 1. **Avatar do Agente**
Mostra estado emocional atual com emoji dinâmico:
- 🌟 EM FLUXO (verde)
- 😴 FATIGADO (vermelho)
- 🤖 ATIVO (amarelo)
- 💭 OCIOSO (cinza)

#### 2. **Métricas em Tempo Real**
- Tempo ocioso
- Urgência do drive dominante
- Número de ações autônomas
- Estado de fluxo (ativo/inativo)

#### 3. **Visualizações**
- **Gauge de Estado Emocional**: Valência geral (0-1)
- **Barras de Métricas Cognitivas**: Load, foco, velocidade, fadiga
- **Scatter de Fluxo de Pensamentos**: Timeline com tipos e importância
- **Pizza de Distribuição de Memória**: Episódica vs Semântica vs Associações

#### 4. **Tabela de Pensamentos Recentes**
Lista os últimos pensamentos com:
- Tipo (reflection, planning, etc.)
- Conteúdo (truncado)
- Importância (0-1)
- Confiança (0-1)
- Se gerou ação (✓ ou ○)

---

## 📁 Estrutura de Arquivos

```
agent/
├── autonomy/
│   ├── __init__.py          # exports do módulo
│   └── intrinsic.py         # sistema completo de autonomia
│       ├── DriveType        # enum dos 7 drives
│       ├── ThoughtType      # enum dos 7 tipos de pensamento
│       ├── IntrinsicDrive   # classe de drive individual
│       ├── SpontaneousThought # classe de pensamento
│       ├── MetaCognitiveState # estado meta-cognitivo
│       ├── IntrinsicMotivationEngine # motor de motivação
│       ├── SpontaneousThoughtGenerator # gerador de pensamentos
│       ├── MetaCognitionMonitor # monitor de performance
│       ├── AutonomousThinkingLoop # loop principal
│       └── create_autonomy_system() # factory function
│
├── ui/
│   ├── __init__.py          # exports do módulo
│   └── dashboard.py         # interface Streamlit
│       ├── render_agent_avatar()
│       ├── render_autonomy_status()
│       ├── render_recent_thoughts()
│       ├── render_performance_metrics()
│       └── run_dashboard_demo()
│
└── demo_end_to_end.py       # demonstração completa
```

---

## 🚀 Como Usar

### Executar Demo de Autonomia

```bash
cd /workspace/agent

# Demo de 30 segundos (default)
python demo_end_to_end.py

# Demo customizada (60 segundos)
python demo_end_to_end.py --duration 60

# Mostrar resumo da arquitetura
python demo_end_to_end.py --summary
```

### Executar Dashboard

```bash
# Instalar dependências se necessário
pip install streamlit plotly pandas

# Rodar dashboard
streamlit run agent/ui/dashboard.py
```

### Integrar com Agente Existente

```python
from agent.autonomy import create_autonomy_system

# Cria sistema de autonomia
autonomy = create_autonomy_system(
    agent_core=meu_agente,
    memory_manager=gerenciador_memoria,
    conscience_engine=engine_etica
)

# Inicia loop em background
import asyncio
asyncio.create_task(autonomy.run_autonomous_loop())

# Para parar
autonomy.stop()
```

---

## 🔍 Exemplo de Saída da Demo

```
======================================================================
🤖 DEMONSTRAÇÃO DO AGENTE AUTÔNOMO - FASE 6
======================================================================

🔧 Inicializando componentes...
   ✓ Sistema de autonomia criado
   ✓ Intervalo de pensamento: 2.0s
   ✓ Limiar de inatividade: 5.0s

🚀 Iniciando loop de pensamento autônomo...

💬 [0.5s] Input externo recebido

📊 [5.0s] Status:
   Drive dominante: curiosity
   Urgência: 0.65
   Estado de fluxo: False
   Ações autônomas: 2

  📝 Memória adicionada: Por que isso funciona dessa maneira?...

💬 [10.2s] Input externo recebido

...

======================================================================
📋 RELATÓRIO FINAL
======================================================================

✅ Duração: 30s
✅ Ações autônomas geradas: 12
✅ Memórias criadas: 8

💭 Últimos pensamentos:
   • [question] Por que isso funciona dessa maneira?...
   • [association] Isso me lembra aquilo que aprendi antes...
   • [creative_insight] E se combinarmos essas ideias de forma inusitada?...

🎯 Estado meta-cognitivo final:
   • Carga cognitiva: 0.45
   • Qualidade do foco: 0.82
   • Nível de fadiga: 0.23
   • Estado de fluxo: False

✨ Demonstração concluída com sucesso!
```

---

## 🎯 Personalização

### Customizar Personalidade do Agente

No arquivo `intrinsic.py`, modifique os pesos dos drives:

```python
self.personality_weights = {
    DriveType.CURIOSITY: 1.5,      # Mais curioso
    DriveType.EFFICIENCY: 0.8,     # Menos focado em eficiência
    DriveType.CONNECTION: 1.2,     # Mais social
    DriveType.CREATION: 1.3,       # Mais criativo
    DriveType.ORGANIZATION: 0.7,   # Menos organizador
    DriveType.SELF_IMPROVEMENT: 1.4, # Focado em auto-melhoria
    DriveType.REST: 0.5            # Dorme menos
}
```

### Ajustar Comportamento

```python
# Intervalo entre ciclos de pensamento
autonomy.thinking_interval = 3.0  # segundos

# Tempo de inatividade para iniciar autonomia
autonomy.idle_threshold = 60.0  # segundos

# Probabilidades de tipos de pensamento
weights = {
    ThoughtType.REFLECTION: 0.30,      # Aumentar reflexão
    ThoughtType.CREATIVE_INSIGHT: 0.10 # Manter criatividade
}
```

---

## 📊 Estatísticas da Fase 6

| Métrica | Valor |
|---------|-------|
| Linhas de código | ~1,100 |
| Classes principais | 9 |
| Enums | 2 |
| Funções factory | 1 |
| Componentes UI | 8 |
| Visualizações | 5 |

---

## 🔮 Próximos Passos Sugeridos

1. **Integração Real**: Conectar com memória e ética reais do agente
2. **Persistência**: Salvar/restaurar estado de drives e pensamentos
3. **API REST**: Expor status via endpoint HTTP
4. **WebSocket**: Dashboard em tempo real sem polling
5. **Mobile**: Versão responsiva para celular
6. **Notificações**: Alertas quando ações importantes ocorrerem
7. **Histórico**: Log completo de todas as ações autônomas
8. **Configuração YAML**: Externalizar personalidade e parâmetros

---

## ✅ Checklist de Implementação

- [x] Drives internos com dinâmica temporal
- [x] Gerador de pensamentos espontâneos
- [x] Monitor de meta-cognição
- [x] Loop de autonomia assíncrono
- [x] Integração com ética (consciência)
- [x] Registro em memória
- [x] Dashboard Streamlit completo
- [x] Visualizações interativas
- [x] Demo end-to-end funcional
- [x] Documentação detalhada

---

**Status da Fase 6**: ✅ **COMPLETA**

Próxima fase sugerida: **Fase 7 - Aprendizado Contínuo & Auto-Evolução**
