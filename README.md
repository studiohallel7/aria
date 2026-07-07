# 🤖 Autonomous AI Agent

Single-core autonomous AI agent with multi-provider LLM support, intelligent API rotation, and persistent memory.

## 🎯 Features

- **Multi-Provider Support**: OpenAI, OpenRouter, OpenCode, and custom providers
- **Intelligent API Rotation**: Automatic account switching based on usage thresholds
- **Persistent Memory**: Short-term and long-term memory systems
- **Autonomous Operation**: Continuous loop with self-initiative capabilities
- **Safety First**: Action classification (safe/moderate/critical) with confirmation levels
- **CLI Interface**: Full control via command-line interface

## 📁 Project Structure

```
agent/
├── cmd/              # CLI entry points
├── core/             # Agent brain (loop, cognition, state, autonomy)
├── infra/            # External integrations (LLM providers, accounts, tools)
├── memory/           # Memory management system
├── safety/           # Security and guardrails
├── config/           # Configuration files
├── data/agent/       # Runtime data (not versioned)
└── tests/            # Test suites
```

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Copy environment template
cp .env.example .env

# Edit with your API keys
nano .env
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Providers

```bash
# List configured providers
python -m cmd.agent_cli.main providers --list

# Add a new provider interactively
python -m cmd.agent_cli.main providers --add
```

### 4. Configure Accounts

```bash
# List accounts
python -m cmd.agent_cli.main accounts --list

# Add new API account
python -m cmd.agent_cli.main accounts --add
```

### 5. Run the Agent

```bash
# Start in work mode (follows user commands)
python -m cmd.agent_cli.main run --mode work

# Start in free mode (autonomous exploration)
python -m cmd.agent_cli.main run --mode free

# Add a task
python -m cmd.agent_cli.main add "Analyze the codebase structure"

# Check status
python -m cmd.agent_cli.main status
```

## 📋 CLI Commands

| Command | Description |
|---------|-------------|
| `run` | Start the agent |
| `add` | Add a task to the queue |
| `status` | Show agent status |
| `logs` | View logs |
| `config` | Manage configuration |
| `memory` | Manage agent memory |
| `accounts` | Manage API accounts |
| `providers` | Manage LLM providers |
| `health` | System health check |
| `version` | Show version |

## ⚙️ Configuration

### Providers (`config/providers.yaml`)

Configure LLM providers and models:

```yaml
providers:
  - name: openai
    enabled: true
    models:
      - id: gpt-4o
        capabilities: [text, vision, reasoning]
        cost_per_1k_input: 0.005
        priority: 1
```

### Accounts (`config/accounts.yaml`)

Manage multiple API accounts for rotation:

```yaml
accounts:
  openai:
    - id: account_1
      api_key_env: OPENAI_API_KEY_1
      monthly_budget: 60.00
      priority: 1
```

### Settings (`config/settings.yaml`)

Global agent settings including safety, monitoring, and performance.

## 🔐 Safety Levels

Actions are classified by risk:

- 🟢 **Safe**: Auto-executed (e.g., read files, search)
- 🟡 **Moderate**: Logged, may require confirmation (e.g., write files)
- 🔴 **Critical**: Always requires confirmation (e.g., shell commands, network)

## 🧠 Agent Modes

### Work Mode
- Follows user commands strictly
- No autonomous initiatives outside scope
- Best for focused tasks

### Free Mode
- Autonomous exploration
- Self-directed learning
- Memory writing and organization
- Curiosity-driven actions

## 🔄 API Rotation

The agent automatically rotates between API accounts based on:

- Usage thresholds (70%, 85%, 95%)
- Cost optimization
- Success/failure rates
- Latency considerations

## 📊 Monitoring

Built-in telemetry tracks:

- CPU/Memory/Disk usage
- API response times
- Token consumption
- Cost tracking
- Error rates

## 🛠️ Development

```bash
# Run tests
pytest

# Run in development mode
./scripts/run_dev.sh

# Validate configuration
python -m cmd.agent_cli.main config --validate
```

## 📝 Adding Custom Providers

1. Use the interactive CLI:
   ```bash
   python -m cmd.agent_cli.main providers --add
   ```

2. Or edit `config/providers.yaml` manually:
   ```yaml
   - name: my-provider
     enabled: true
     type: openai_compatible
     base_url: https://api.my-provider.com/v1
     api_key_env: MY_PROVIDER_KEY
     models:
       - id: my-model
         capabilities: [text]
         cost_per_1k_input: 0.001
         priority: 1
   ```

## 📄 License

MIT License

## 🤝 Contributing

See `docs/roadmap.md` for planned features and improvements.
