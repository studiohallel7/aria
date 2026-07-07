"""Providers management command - Add, list, and test LLM providers interactively"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any

CONFIG_DIR = Path(__file__).parent.parent.parent / "config"
PROVIDERS_FILE = CONFIG_DIR / "providers.yaml"


def load_providers() -> Dict[str, Any]:
    """Load providers configuration"""
    if not PROVIDERS_FILE.exists():
        return {"providers": [], "settings": {}}
    
    with open(PROVIDERS_FILE, 'r') as f:
        return yaml.safe_load(f)


def save_providers(config: Dict[str, Any]):
    """Save providers configuration"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(PROVIDERS_FILE, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)


def add_provider_interactive():
    """Add a new provider interactively"""
    print("\n=== Add New LLM Provider ===\n")
    
    config = load_providers()
    
    # Get provider basic info
    name = input("Provider name (e.g., my-custom-provider): ").strip()
    if not name:
        print("❌ Name is required")
        return
    
    # Check if already exists
    for p in config.get("providers", []):
        if p.get("name") == name:
            print(f"❌ Provider '{name}' already exists")
            return
    
    # Provider type
    print("\nProvider types:")
    print("  1. openai (OpenAI API compatible)")
    print("  2. openrouter (OpenRouter)")
    print("  3. anthropic (Anthropic Claude)")
    print("  4. custom (Custom implementation)")
    
    type_choice = input("\nSelect type [1-4] (default: 1): ").strip() or "1"
    type_map = {"1": "openai", "2": "openrouter", "3": "anthropic", "4": "custom"}
    provider_type = type_map.get(type_choice, "openai")
    
    # Base URL
    default_urls = {
        "openai": "https://api.openai.com/v1",
        "openrouter": "https://openrouter.ai/api/v1",
        "anthropic": "https://api.anthropic.com/v1",
    }
    default_url = default_urls.get(provider_type, "")
    base_url = input(f"Base URL [{default_url}]: ").strip() or default_url
    
    # API Key env var
    api_key_env = input("API Key environment variable (e.g., MY_API_KEY): ").strip()
    if not api_key_env:
        print("⚠️  No API key env var specified. You'll need to set it manually.")
    
    # Models
    models = []
    print("\n--- Add Models ---")
    while True:
        model_id = input("\nModel ID (or Enter to finish): ").strip()
        if not model_id:
            break
        
        print("Capabilities (comma-separated):")
        print("  Options: text, vision, code, reasoning, debugging, refactoring")
        caps_input = input("Capabilities [text]: ").strip() or "text"
        capabilities = [c.strip() for c in caps_input.split(",")]
        
        cost_in = input("Cost per 1K input tokens (USD) [0.001]: ").strip() or "0.001"
        cost_out = input("Cost per 1K output tokens (USD) [0.002]: ").strip() or "0.002"
        max_ctx = input("Max context length [32000]: ").strip() or "32000"
        priority = input("Priority [1] (lower = higher priority): ").strip() or "1"
        
        models.append({
            "id": model_id,
            "capabilities": capabilities,
            "cost_per_1k_input": float(cost_in),
            "cost_per_1k_output": float(cost_out),
            "max_context": int(max_ctx),
            "priority": int(priority)
        })
    
    if not models:
        print("⚠️  No models added. Provider must have at least one model.")
        return
    
    # Create provider entry
    provider = {
        "name": name,
        "enabled": True,
        "type": provider_type,
        "base_url": base_url,
    }
    
    if api_key_env:
        provider["api_key_env"] = api_key_env
    
    provider["models"] = models
    
    # Add to config
    if "providers" not in config:
        config["providers"] = []
    
    config["providers"].append(provider)
    save_providers(config)
    
    print(f"\n✅ Provider '{name}' added successfully!")
    print(f"   Models: {len(models)}")
    print(f"\n⚠️  Remember to set the environment variable: export {api_key_env}=your-key")


def list_providers():
    """List all configured providers"""
    config = load_providers()
    providers = config.get("providers", [])
    
    if not providers:
        print("\nNo providers configured.\n")
        print("Use 'python -m cmd.agent_cli.main providers --add' to add one.\n")
        return
    
    print("\n=== Configured LLM Providers ===\n")
    
    for i, provider in enumerate(providers, 1):
        status = "🟢" if provider.get("enabled", False) else "🔴"
        print(f"{i}. {status} {provider['name']} ({provider['type']})")
        print(f"   URL: {provider.get('base_url', 'N/A')}")
        
        if provider.get('api_key_env'):
            has_key = os.getenv(provider['api_key_env']) is not None
            key_status = "✅" if has_key else "❌"
            print(f"   API Key: {key_status} ({provider['api_key_env']})")
        
        models = provider.get("models", [])
        if models:
            print(f"   Models ({len(models)}):")
            for model in models[:5]:  # Show first 5
                caps = ", ".join(model.get("capabilities", []))
                print(f"     • {model['id']} [{caps}]")
            if len(models) > 5:
                print(f"     ... and {len(models) - 5} more")
        
        print()


def test_model(model_id: str):
    """Test a specific model"""
    print(f"\n=== Testing Model: {model_id} ===\n")
    
    config = load_providers()
    
    # Find the model
    found = False
    for provider in config.get("providers", []):
        for model in provider.get("models", []):
            if model["id"] == model_id:
                found = True
                
                # Check if provider is enabled
                if not provider.get("enabled", False):
                    print(f"❌ Provider '{provider['name']}' is disabled")
                    return
                
                # Check API key
                api_key_env = provider.get("api_key_env")
                if api_key_env and not os.getenv(api_key_env):
                    print(f"❌ API key not set: {api_key_env}")
                    print(f"   Set it with: export {api_key_env}=your-key")
                    return
                
                print(f"✅ Model found in provider: {provider['name']}")
                print(f"   Capabilities: {', '.join(model.get('capabilities', []))}")
                print(f"   Max context: {model.get('max_context', 'N/A')}")
                print(f"   Cost: ${model.get('cost_per_1k_input', 0)}/1K input, ${model.get('cost_per_1k_output', 0)}/1K output")
                
                # Try a simple API call
                print("\n🔄 Running test request...")
                try:
                    from infra.llm.client import LLMClient
                    client = LLMClient()
                    
                    response = client.chat(
                        model=model_id,
                        messages=[{"role": "user", "content": "Respond with exactly: TEST_OK"}],
                        max_tokens=10
                    )
                    
                    if "TEST_OK" in response.content:
                        print(f"✅ Test PASSED")
                        print(f"   Response time: {response.latency_ms}ms")
                        print(f"   Tokens used: {response.usage}")
                    else:
                        print(f"⚠️  Test completed but unexpected response")
                        print(f"   Got: {response.content[:100]}")
                        
                except ImportError:
                    print("⚠️  LLM client not yet implemented. Manual testing required.")
                except Exception as e:
                    print(f"❌ Test FAILED: {str(e)}")
                
                return
    
    if not found:
        print(f"❌ Model '{model_id}' not found in configuration")


def compare_models(model_ids: list):
    """Compare multiple models"""
    print("\n=== Model Comparison ===\n")
    
    config = load_providers()
    
    models_data = []
    for provider in config.get("providers", []):
        for model in provider.get("models", []):
            if model["id"] in model_ids:
                models_data.append({
                    "provider": provider["name"],
                    **model
                })
    
    if not models_data:
        print("No matching models found\n")
        return
    
    if len(models_data) < 2:
        print("Need at least 2 models to compare\n")
        return
    
    # Print comparison table
    print(f"{'Model':<40} {'Cost In':<10} {'Cost Out':<10} {'Context':<12} {'Caps'}")
    print("-" * 90)
    
    for m in sorted(models_data, key=lambda x: x.get("cost_per_1k_input", 0)):
        caps = ", ".join(m.get("capabilities", [])[:3])
        print(f"{m['id']:<40} ${m.get('cost_per_1k_input', 0):<9.4f} ${m.get('cost_per_1k_output', 0):<9.4f} {m.get('max_context', 0):<12,} {caps}")
    
    print()


def manage_providers(args):
    """Main entry point for providers command"""
    if args.list:
        list_providers()
    elif args.add:
        add_provider_interactive()
    elif args.test:
        test_model(args.test)
    elif args.compare:
        compare_models(args.compare)
    else:
        print("Use --list, --add, --test, or --compare")
