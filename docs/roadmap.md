# Roadmap do Agente Autônomo

## ✅ Fase 1: Fundação (Completo)

- [x] Estrutura de diretórios
- [x] Configuração YAML (providers, accounts, settings)
- [x] CLI funcional
- [x] Sistema de providers multiplataforma
- [x] Gerenciamento de contas com rotação
- [x] Comandos básicos de gerenciamento

## 🚧 Fase 2: Núcleo Cognitivo (Em Progresso)

### Loop Principal
- [ ] Implementar `core/loop/main_loop.py`
- [ ] Sistema de gatilhos múltiplos
- [ ] Controle de estado (idle, thinking, executing, exploring)
- [ ] Prioridade de tarefas (usuário > interno)

### Cognição
- [ ] `core/cognition/thinking.py` - Pensamento interno
- [ ] `core/cognition/planner.py` - Planejamento em etapas
- [ ] `core/cognition/reflection.py` - Reflexão pós-ação
- [ ] `core/cognition/intention.py` - Sistema de intenção

### Estado e Contexto
- [ ] `core/state/agent_state.py` - Estado persistente
- [ ] `core/state/context_manager.py` - Gerenciamento de contexto

### Autonomia
- [ ] `core/autonomy/mode_manager.py` - Trabalho vs Livre
- [ ] `core/autonomy/priorities.py` - Sistema de prioridades
- [ ] `core/autonomy/triggers.py` - Gatilhos do loop

## 🔧 Fase 3: Infraestrutura LLM

### Providers
- [ ] `infra/llm/providers/openai.py` - Cliente OpenAI
- [ ] `infra/llm/providers/openrouter.py` - Cliente OpenRouter
- [ ] `infra/llm/providers/opencode.py` - Cliente OpenCode
- [ ] `infra/llm/router.py` - Roteador inteligente
- [ ] `infra/llm/client.py` - Interface unificada

### Contas
- [ ] `infra/accounts/manager.py` - Rotação de contas
- [ ] `infra/accounts/quota_tracker.py` - Tracking de consumo
- [ ] `infra/accounts/healthcheck.py` - Verificação de saúde

### Ferramentas
- [ ] `infra/tools/llm_tools.py` - LLMs como ferramentas
- [ ] `infra/tools/web.py` - Navegação web
- [ ] `infra/tools/filesystem.py` - Operações de arquivo
- [ ] `infra/tools/shell.py` - Comandos shell

### Monitoramento
- [ ] `infra/monitoring/telemetry.py` - Telemetria
- [ ] `infra/monitoring/logger.py` - Logging estruturado

## 🧠 Fase 4: Memória

- [ ] `memory/manager.py` - Gerenciador principal
- [ ] `memory/short_term.py` - Memória de curto prazo
- [ ] `memory/long_term.py` - Memória de longo prazo
- [ ] `memory/embeddings.py` - Embeddings para busca
- [ ] `memory/indexer.py` - Indexação e recuperação

## 🛡️ Fase 5: Segurança

- [ ] `safety/classifier.py` - Classificação de risco
- [ ] `safety/policies.py` - Políticas de segurança
- [ ] `safety/guardrails.py` - Guardrails de execução

## 📊 Funcionalidades Futuras

### Melhorias de Cognição
- [ ] Aprendizado por reforço baseado em feedback
- [ ] Meta-cognição (pensar sobre o pensamento)
- [ ] Transfer learning entre tarefas similares
- [ ] Detecção de padrões em execuções passadas

### Expansão de Tools
- [ ] Integração com GitHub API
- [ ] Leitura de PDFs e documentos
- [ ] Execução de código sandboxed
- [ ] Integração com Slack/Discord
- [ ] Web scraping avançado

### Memória Avançada
- [ ] Busca semântica com vetores
- [ ] Compressão automática de memórias antigas
- [ ] Linking entre memórias relacionadas
- [ ] Export/import de memória

### Multi-Agent (Futuro Distante)
- [ ] Coordenação entre múltiplos agentes
- [ ] Divisão de tarefas complexas
- [ ] Consenso distribuído
- [ ] Especialização por domínio

## 🎯 Métricas de Sucesso

1. **Autonomia**: Agente opera 80% do tempo sem intervenção
2. **Eficiência**: Rotação de APIs reduz custos em 30%
3. **Confiabilidade**: 99% uptime em modo work
4. **Segurança**: Zero execuções não autorizadas de ações críticas
5. **Memória**: Recall >90% em buscas de contexto

## 📝 Decisões de Arquitetura (ADRs)

Ver `docs/decisions.md` para decisões arquiteturais documentadas.

## 🔗 Dependências Externas Sugeridas

```yaml
# requirements.txt futuro
openai>=1.0.0
anthropic>=0.18.0
httpx>=0.25.0
pyyaml>=6.0
rich>=13.0.0      # Terminal UI
typer>=0.9.0      # CLI framework
pydantic>=2.0.0   # Validação de dados
aiosqlite>=0.19.0 # Memória persistente
sentence-transformers>=2.2.0  # Embeddings
psutil>=5.9.0     # Monitoramento de sistema
```

## 🧪 Testes

- [ ] Tests/unit/ - Testes unitários
- [ ] tests/integration/ - Testes de integração
- [ ] tests/simulation/ - Simulação de comportamento

## 📚 Documentação Pendente

- [ ] Guia de arquitetura detalhado
- [ ] API reference
- [ ] Tutoriais de uso
- [ ] Exemplos de casos de uso
- [ ] FAQ e troubleshooting
