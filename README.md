# 🤖 Agente Autônomo - Sistema Cognitivo Completo

Um framework avançado para agentes autônomos com pensamento contínuo, memória holográfica e ética constitutiva.

## 🏗️ Arquitetura em 5 Fases

| Fase | Componente | Descrição | Status |
|------|-----------|-----------|--------|
| **1** | Fundação | Configuração YAML, CLI, providers | ✅ |
| **2** | Núcleo Cognitivo | Thinking, Planning, Reflection, Intention | ✅ |
| **3** | Infraestrutura LLM | Router, Tools, Accounts, Monitoring | ✅ |
| **4** | Memória Avançada | Grafo holográfico, consolidação, subconsciente | ✅ |
| **5** | Ética Constitutiva | Constituição, consciência, alignment | ✅ |

## 🚀 Instalação

```bash
cd /workspace
pip install -e .
```

## 💡 Uso Básico

```python
from agent import create_agent

# Criar agente
agent = create_agent(name="Aria")

# Iniciar modo autônomo
agent.start_autonomous_mode()
```

## 📁 Estrutura do Projeto

```
/workspace/agent/
├── core/               # Núcleo cognitivo
│   ├── cognition/      # Thinking, Planning, Reflection
│   ├── state/          # Gerenciamento de estado
│   ├── autonomy/       # Mode manager, triggers
│   └── loop/           # Main loop do agente
├── infra/              # Infraestrutura
│   ├── llm/            # Router, providers, client
│   ├── tools/          # Web, filesystem, shell
│   ├── accounts/       # Gestão de contas e quotas
│   └── monitoring/     # Logger, telemetry
├── memory/             # Memória avançada
│   └── manager.py      # Grafo holográfico
├── safety/             # Ética constitutiva
│   ├── constitution.py # Princípios morais
│   ├── conscience.py   # Engine de deliberação
│   └── alignment.py    # Verificação de alinhamento
└── config/             # Configurações YAML
```

## 🧠 Pensamento Autônomo

O agente pensa continuamente através de:

1. **Drive Interno**: Motivação intrínseca baseada em curiosidade e propósito
2. **Boredom Detection**: Detecta ociosidade e gera novas intenções
3. **Working Set**: Mantém contexto ativo na memória de trabalho
4. **Reflection Loop**: Aprende com cada ação executada

## 🛡️ Ética Constitutiva

Diferente de guardrails externos, o agente possui:

- **Constituição Moral**: Princípios ponderados (CRITICAL, HIGH, MEDIUM, LOW)
- **Consciência Ativa**: Delibera em 6 passos antes de agir
- **Alignment Contínuo**: Verifica cada ação contra princípios
- **Transparência**: Todo raciocínio é registradado e auditável

## 📊 Métricas do Projeto

- **Total de código**: ~17,000+ linhas Python
- **Arquivos**: 100+ módulos
- **Testes**: Suite de integração completa
- **Fases completas**: 5/5 ✅

## 📖 Documentação

- [Roadmap](docs/roadmap.md)
- [Arquitetura de Pensamento Autônomo](docs/autonomous_thinking_architecture.md)
- [Resumo Fases 1-2](docs/phase1_2_summary.md)
- [Fase 2 Completa](docs/phase2_complete.md)

## 🔧 CLI Commands

```bash
# Ver status do agente
agent-cli status

# Iniciar agente
agent-cli start

# Configurar provider
agent-cli config set-provider openai

# Ver logs
agent-cli logs --tail 100
```

## 🎯 Próximos Passos

1. **Interface Gráfica**: Dashboard web para monitoramento
2. **Pensamento Autônomo Profundo**: Implementar fluxo de consciência contínuo
3. **Multi-Agent**: Suporte para colaboração entre agentes
4. **Plugin System**: Extensibilidade via plugins

## 📄 Licença

MIT License
