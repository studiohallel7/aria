# Implementação Real - Executor de Loop e Integração LLM com OpenCode

## Resumo da Implementação

Esta documentação descreve a implementação real do executor de looping e integração com LLM, focando no provider OpenCode conforme solicitado.

## 1. Configuração do OpenCode Provider

### Arquivo: `/workspace/config/providers.yaml`

```yaml
opencode:
  enabled: true
  type: opencode
  base_url: https://opencode.ai/zen/v1/chat/completions
  models:
    - name: deepseek-v4-flash-free
      capabilities: [code, debugging, refactoring, text]
      cost_per_1k_input: 0.0
      cost_per_1k_output: 0.0
      max_context: 64000
      priority: 1
    - name: gpt-5.5
      capabilities: [code, text, vision, reasoning]
      cost_per_1k_input: 0.0
      cost_per_1k_output: 0.0
      max_context: 128000
      priority: 2
```

**Mudanças principais:**
- Provider habilitado (`enabled: true`)
- URL atualizada para endpoint correto: `https://opencode.ai/zen/v1/chat/completions`
- Modelos configurados: `deepseek-v4-flash-free` e `gpt-5.5`
- Formato changed de lista para dicionário para compatibilidade com router
- Custo zero (modelos gratuitos)

### Arquivo: `/workspace/config/accounts.yaml`

```yaml
opencode:
  - id: oc_account_1
    name: "OpenCode Primary"
    api_key_env: OPENCODE_API_KEY
    enabled: true
    monthly_budget: 0.0
    current_usage: 0.0
    reset_date: "2025-02-01"
    priority: 1
    quota:
      daily_limit_usd: 0.0
      current_daily_spent: 0.0

rotation:
  strategy: priority_based
```

**Mudanças:**
- Estratégia de rotação alterada para `priority_based`
- Budget zero (serviço gratuito)
- Quota configurada

## 2. Provider OpenCode Implementation

### Arquivo: `/workspace/agent/infra/llm/providers/opencode.py`

```python
class OpencodeProvider(LLMProvider):
    """Opencode LLM provider - Suporte para DeepSeek V4 Flash Free e GPT-5.5."""
    
    name = "opencode"
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENCODE_API_KEY", "")
        self.base_url = base_url or "https://opencode.ai/zen/v1/chat/completions"
        
        self._models = {
            "deepseek-v4-flash-free": {"purpose": "code", "priority": 1},
            "gpt-5.5": {"purpose": "general", "priority": 2},
        }
    
    def _estimate_cost(self, model: str, tokens: int) -> float:
        """OpenCode oferece modelos gratuitos."""
        return 0.0
```

**Features:**
- URL correta conforme documentação
- Modelos atualizados
- Custo zero implementado
- API key opcional (pode vir de env)

## 3. Router LLM

### Arquivo: `/workspace/agent/infra/llm/router.py`

O router já suporta múltiplos providers e faz:
- Seleção automática de modelo baseado em propósito
- Fallback chain em caso de falha
- Health check de providers
- Balanceamento de carga

**Modelos disponíveis após configuração:**
```
- openrouter/anthropic/claude-3.5-sonnet (priority: 1)
- openrouter/google/gemini-pro-1.5 (priority: 2)
- openrouter/meta-llama/llama-3.1-405b-instruct (priority: 3)
- opencode/deepseek-v4-flash-free (priority: 1) ⭐
- opencode/gpt-5.5 (priority: 2) ⭐
```

## 4. Action Executor Real

### Arquivo: `/workspace/agent/core/loop/action_executor.py`

Implementação completa com:

**Ações suportadas:**
1. `file_operation` - Operações de arquivo (read, write, list, search)
2. `shell_command` - Execução de comandos shell
3. `web_search` - Busca na web
4. `code_analysis` - Análise de código com LLM
5. `respond_to_user` - Respostas ao usuário
6. `log_insight` - Insights de logs
7. `fix_issue` - Correção de issues
8. `optimize_system` - Otimização do sistema

**Features implementadas:**
- Extração de parâmetros com LLM (usa OpenCode quando disponível)
- Fallback para extração simples sem LLM
- Validação de segurança para comandos shell
- Rastreamento de tokens usados
- Histórico de execuções
- Logging detalhado

**Melhoria recente:**
```python
def _extract_file_params(self, description: str, context: Dict) -> Optional[Dict]:
    # Usa contexto direto se disponível (evita chamada LLM desnecessária)
    if context and ('operation' in context or 'path' in context):
        params = {
            'operation': context.get('operation', 'read'),
            'path': context.get('path', '.'),
            'content': context.get('content', ''),
            'pattern': context.get('pattern', '*')
        }
        return params
    
    # Otherwise usa LLM para extrair
    ...
```

## 5. Ferramentas Disponíveis

Via `LLMTools`:
- `read_file` - Ler arquivos
- `write_file` - Escrever arquivos
- `list_directory` - Listar diretórios
- `search_files` - Buscar arquivos
- `execute_command` - Executar comandos shell
- `fetch_webpage` - Fetch de páginas web
- `search_web` - Busca na web

## 6. Testes Realizados

### Teste 1: Listagem de diretório
```python
executor.execute_action(
    action_type='file_operation',
    description='listar diretório',
    context={'operation': 'list', 'path': '/workspace/agent/core'}
)
# Result: Success=True, Tool used: fs_list
```

### Teste 2: Leitura de arquivo
```python
executor.execute_action(
    action_type='file_operation',
    description='ler arquivo',
    context={'operation': 'read', 'path': '/workspace/agent/core/loop/main_loop.py'}
)
# Result: Success=True, Tool used: fs_read
```

### Teste 3: Router LLM
```python
router = LLMRouter()
model = router.select_model(purpose='code')
# Result: opencode/deepseek-v4-flash-free (prioridade 1)
```

## 7. Como Usar

### Setup da API Key
```bash
export OPENCODE_API_KEY="sua-api-key-aqui"
```

### Uso Programático
```python
from agent.core.loop.action_executor import ActionExecutor
from agent.infra.llm.router import LLMRouter
from agent.infra.llm.client import LLMMessage

# Executor
executor = ActionExecutor()
result = executor.execute_action(
    action_type='file_operation',
    description='Listar arquivos',
    context={'operation': 'list', 'path': '/workspace/agent'}
)

# LLM Router
router = LLMRouter()
messages = [LLMMessage(role='user', content='Olá')]
response = router.chat_completion(
    messages=messages,
    model='opencode/deepseek-v4-flash-free',
    purpose='code'
)
```

## 8. Próximos Passos (Fora do Escopo Atual)

Conforme discutido, estes itens ficarão para implementação futura:
- [ ] Busca web real (DuckDuckGo API)
- [ ] Interface unificada (GUI + CLI + Voz)
- [ ] Modelo VTuber funcional
- [ ] Integrações de voz (STT/TTS)
- [ ] Alinhamento ético completo

## 9. Status da Implementação

✅ **Completo:**
- Configuração OpenCode (providers.yaml, accounts.yaml)
- Provider Opencode atualizado
- Router LLM funcional
- Action Executor real implementado
- Extração de parâmetros otimizada
- Ferramentas de filesystem operacionais
- Comandos shell com validação de segurança
- Integração LLM para decisões complexas

⏳ **Pendente:**
- Busca web real
- Interface unificada
- VTuber
- Voz

## 10. Referências

- OpenCode API: https://opencode.ai/zen/v1/chat/completions
- Model ID format: `opencode/<model-id>` (ex: `opencode/deepseek-v4-flash-free`)
- Documentação: `@ai-sdk/openai-compatible`

---

**Data da Implementação:** 2025
**Foco:** Executor real de looping + Integração LLM OpenCode
