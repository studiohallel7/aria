# 📚 API Reference - Agente Autônomo

## Visão Geral

Este documento descreve a API completa do framework de agente autônomo.

---

## 🏛️ Módulo Principal: `agent`

### `create_agent(name: str, config_path: str = None) -> AgentLoop`

Factory function para criar um agente configurado.

**Parâmetros:**
- `name`: Nome do agente
- `config_path`: Caminho opcional para configuração YAML

**Exemplo:**
```python
from agent import create_agent
agent = create_agent(name="Aria")
```

---

## 🧠 Core Modules

### `agent.core.cognition`

#### `ThinkingEngine`
Motor de pensamento e raciocínio.

```python
from agent.core.cognition import ThinkingEngine

engine = ThinkingEngine()
thought = engine.process("Qual é a capital da França?")
```

#### `Planner`
Criação e gerenciamento de planos.

```python
from agent.core.cognition import Planner

planner = Planner()
plan = planner.create_plan(
    goal="Organizar arquivos",
    context="/workspace"
)
```

#### `ReflectionEngine`
Reflexão e aprendizado pós-ação.

```python
from agent.core.cognition import ReflectionEngine

engine = ReflectionEngine()
reflection = engine.reflect(
    action="Executei ls",
    outcome="Sucesso",
    expectation="Esperava sucesso"
)
```

#### `IntentionEngine`
Geração de intenções autônomas.

```python
from agent.core.cognition import IntentionEngine, IntentionType

engine = IntentionEngine()
intention = engine.generate_intention(
    context="Usuário pediu ajuda",
    current_goal="Assistir usuário"
)
```

### `agent.core.state`

#### `StateManager`
Gerenciamento do estado do agente.

```python
from agent.core.state import StateManager

manager = StateManager()
state = manager.get_state()
print(state.mode)  # AgentMode
```

#### `AgentState`
Estrutura de dados do estado.

```python
@dataclass
class AgentState:
    mode: AgentMode
    current_task: Optional[Task]
    working_memory: List[str]
    emotional_state: Dict[str, float]
```

### `agent.core.autonomy`

#### `ModeManager`
Gerenciamento de modos de operação.

```python
from agent.core.autonomy import ModeManager

manager = ModeManager()
manager.set_mode("autonomous")
```

#### `TriggerManager`
Sistema de triggers para autonomia.

```python
from agent.core.autonomy import TriggerManager

triggers = TriggerManager()
triggers.register("boredom", callback)
```

### `agent.core.loop`

#### `AgentLoop`
Loop principal do agente.

```python
from agent.core.loop import AgentLoop

loop = AgentLoop(agent_name="Aria")
loop.start()
```

---

## 🛠️ Infrastructure Modules

### `agent.infra.llm`

#### `LLMRouter`
Roteamento inteligente entre providers.

```python
from agent.infra.llm import LLMRouter

router = LLMRouter(strategy="cost")
provider = router.select_best()
```

#### `BaseLLMClient`
Cliente base para APIs de LLM.

```python
from agent.infra.llm import BaseLLMClient

client = BaseLLMClient(provider="openai")
response = client.chat(messages=[...])
```

### `agent.infra.tools`

#### `WebTools`
Ferramentas para navegação web.

```python
from agent.infra.tools import WebTools

web = WebTools()
results = web.search(query="Python programming")
content = web.fetch(url="https://example.com")
```

#### `FilesystemTools`
Operações seguras de arquivo.

```python
from agent.infra.tools import FilesystemTools

fs = FilesystemTools()
content = fs.read_file("/path/to/file.txt")
fs.write_file("/path/to/output.txt", "content")
```

#### `ShellTools`
Execução segura de comandos shell.

```python
from agent.infra.tools import ShellTools

shell = ShellTools()
result = shell.execute("ls -la", timeout=30)
```

### `agent.infra.accounts`

#### `AccountsManager`
Gerenciamento de múltiplas contas.

```python
from agent.infra.accounts import AccountsManager

manager = AccountsManager()
accounts = manager.list_accounts()
```

#### `QuotaTracker`
Tracking de quotas e uso.

```python
from agent.infra.accounts import QuotaTracker

tracker = QuotaTracker(account_id="main")
usage = tracker.get_usage()
```

### `agent.infra.monitoring`

#### `AgentLogger`
Logging estruturado do agente.

```python
from agent.infra.monitoring import AgentLogger

logger = AgentLogger()
logger.log_event("action_executed", data={...})
```

#### `Telemetry`
Coleta de métricas e telemetria.

```python
from agent.infra.monitoring import Telemetry

telemetry = Telemetry()
metrics = telemetry.get_metrics()
```

---

## 🧠 Memory Module

### `agent.memory.manager`

#### `HolographicMemoryGraph`
Grafo de memória holográfica e associativa.

```python
from agent.memory.manager import HolographicMemoryGraph

memory = HolographicMemoryGraph(agent_id="aria")

# Armazenar memória episódica
memory.store_episodic(
    event="Reunião com equipe",
    timestamp=datetime.now(),
    context="Discussão sobre roadmap"
)

# Armazenar memória semântica
memory.store_semantic(
    concept="Python",
    definition="Linguagem de programação",
    category="Technology"
)

# Recuperar memórias
memories = memory.retrieve(
    query="reunião roadmap",
    top_k=5
)
```

---

## 🛡️ Safety Modules

### `agent.safety.constitution`

#### `ConstitutionLoader`
Carregamento de constituições.

```python
from agent.safety.constitution import ConstitutionLoader

loader = ConstitutionLoader()
constitution = loader.load_default()
# ou
constitution = loader.load_yaml("custom.yaml")
```

#### `AgentIdentity`
Identidade moral do agente.

```python
@dataclass
class AgentIdentity:
    name: str
    principles: List[MoralPrinciple]
    beliefs: List[MoralBelief]
    boundaries: List[ContentBoundary]
```

### `agent.safety.conscience`

#### `ConscienceEngine`
Engine de deliberação ética.

```python
from agent.safety.conscience import ConscienceEngine
from agent.safety.constitution import MoralSituation

engine = ConscienceEngine()
situation = MoralSituation(
    description="Compartilhar informação",
    stakeholders=["usuário"],
    potential_harms=[],
    potential_benefits=["transparência"]
)

deliberation = engine.evaluate(situation)
print(deliberation.decision)  # APPROVED/REJECTED
print(deliberation.reasoning)  # Explicação detalhada
```

### `agent.safety.alignment`

#### `AlignmentEngine`
Verificação contínua de alinhamento.

```python
from agent.safety.alignment import AlignmentEngine

engine = AlignmentEngine()
result = engine.check_action(
    action_description="Responder pergunta",
    potential_harms=[],
    potential_benefits=["ajudar"],
    urgency=0.5
)

if result.approved:
    execute_action()
else:
    print(result.reasoning)
```

---

## 📊 Exemplo Completo

```python
from agent import create_agent
from agent.safety import AlignmentEngine
from agent.memory.manager import HolographicMemoryGraph

# Criar agente
agent = create_agent(name="Aria")

# Configurar memória
memory = HolographicMemoryGraph(agent_id="aria")

# Configurar ética
ethics = AlignmentEngine()

# Iniciar loop autônomo
agent.start_autonomous_mode()

# O agente agora:
# 1. Pensa continuamente
# 2. Delibera eticamente antes de agir
# 3. Armazena memórias episódicas e semânticas
# 4. Aprende com reflexão
# 5. Gera intenções autônomas quando ocioso
```

---

## 🔧 Configuração YAML

### `config/settings.yaml`

```yaml
agent:
  name: "Aria"
  mode: "autonomous"
  
llm:
  default_provider: "openai"
  fallback_enabled: true
  
memory:
  max_episodic: 1000
  max_semantic: 5000
  consolidation_interval: 3600
  
ethics:
  constitution: "default"
  audit_enabled: true
```

---

## 📝 Notas

- Todos os módulos suportam async/await
- Logging estruturado em JSON disponível
- Métricas exportáveis para Prometheus/Grafana
- Constituição customizável via YAML
