"""Accounts management command - Add, list, and manage API accounts"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

CONFIG_DIR = Path(__file__).parent.parent.parent / "config"
ACCOUNTS_FILE = CONFIG_DIR / "accounts.yaml"


def load_accounts() -> Dict[str, Any]:
    """Load accounts configuration"""
    if not ACCOUNTS_FILE.exists():
        return {"accounts": {}, "rotation": {}, "healthcheck": {}}
    
    with open(ACCOUNTS_FILE, 'r') as f:
        return yaml.safe_load(f)


def save_accounts(config: Dict[str, Any]):
    """Save accounts configuration"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(ACCOUNTS_FILE, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)


def add_account_interactive():
    """Add a new API account interactively"""
    print("\n=== Add New API Account ===\n")
    
    config = load_accounts()
    
    # Select provider type
    print("Provider types:")
    print("  1. OpenAI")
    print("  2. OpenRouter")
    print("  3. OpenCode")
    print("  4. Custom")
    
    provider_choice = input("\nSelect provider [1-4] (default: 1): ").strip() or "1"
    provider_map = {"1": "openai", "2": "openrouter", "3": "opencode", "4": "custom"}
    provider_type = provider_map.get(provider_choice, "openai")
    
    # Account details
    account_id = input("Account ID (e.g., my-account-1): ").strip()
    if not account_id:
        print("❌ Account ID is required")
        return
    
    account_name = input("Account name/description: ").strip()
    
    api_key_env = input("API Key environment variable: ").strip()
    if not api_key_env:
        print("❌ API Key env var is required")
        return
    
    # Check if account already exists
    if provider_type in config.get("accounts", {}):
        for acc in config["accounts"][provider_type]:
            if acc.get("id") == account_id:
                print(f"❌ Account '{account_id}' already exists in {provider_type}")
                return
    
    # Budget info
    budget_input = input("Monthly budget (USD) [30.00]: ").strip() or "30.00"
    try:
        monthly_budget = float(budget_input)
    except ValueError:
        print("⚠️  Invalid budget, using default: 30.00")
        monthly_budget = 30.00
    
    reset_date = input("Billing reset date (YYYY-MM-DD): ").strip()
    if not reset_date:
        from datetime import timedelta
        reset_date = (datetime.now().replace(day=1) + timedelta(days=32)).replace(day=1).strftime("%Y-%m-%d")
    
    priority = input("Priority [1] (lower = higher priority): ").strip() or "1"
    
    # Create account entry
    account = {
        "id": account_id,
        "name": account_name,
        "api_key_env": api_key_env,
        "enabled": True,
        "monthly_budget": monthly_budget,
        "current_usage": 0.00,
        "reset_date": reset_date,
        "priority": int(priority)
    }
    
    # Add to config
    if "accounts" not in config:
        config["accounts"] = {}
    
    if provider_type not in config["accounts"]:
        config["accounts"][provider_type] = []
    
    config["accounts"][provider_type].append(account)
    save_accounts(config)
    
    print(f"\n✅ Account added successfully!")
    print(f"   Provider: {provider_type}")
    print(f"   ID: {account_id}")
    print(f"   Budget: ${monthly_budget:.2f}/month")
    print(f"\n⚠️  Remember to set: export {api_key_env}=your-key")


def list_accounts():
    """List all configured accounts"""
    config = load_accounts()
    accounts_by_provider = config.get("accounts", {})
    
    if not accounts_by_provider:
        print("\nNo accounts configured.\n")
        print("Use 'python -m cmd.agent_cli.main accounts --add' to add one.\n")
        return
    
    print("\n=== API Accounts by Provider ===\n")
    
    for provider_type, accounts in accounts_by_provider.items():
        print(f"\n📦 {provider_type.upper()}")
        print("-" * 50)
        
        for acc in accounts:
            status = "🟢" if acc.get("enabled", False) else "🔴"
            
            # Check API key
            api_key_env = acc.get("api_key_env", "")
            has_key = os.getenv(api_key_env) is not None if api_key_env else False
            key_status = "✅" if has_key else "❌"
            
            # Calculate usage percentage
            budget = acc.get("monthly_budget", 0)
            usage = acc.get("current_usage", 0)
            usage_pct = (usage / budget * 100) if budget > 0 else 0
            
            # Usage bar
            bar_length = 20
            filled = int(bar_length * usage_pct / 100)
            bar = "█" * filled + "░" * (bar_length - filled)
            
            print(f"\n  {status} {acc['name']} ({acc['id']})")
            print(f"     API Key: {key_status} ({api_key_env})")
            print(f"     Budget:  ${usage:.2f} / ${budget:.2f} [{bar}] {usage_pct:.1f}%")
            print(f"     Reset:   {acc.get('reset_date', 'N/A')}")
            print(f"     Priority: {acc.get('priority', 'N/A')}")
    
    print("\n")


def show_account_status():
    """Show detailed account usage and health status"""
    config = load_accounts()
    accounts_by_provider = config.get("accounts", {})
    
    print("\n=== Account Status & Health ===\n")
    
    total_budget = 0
    total_usage = 0
    healthy_count = 0
    total_count = 0
    
    for provider_type, accounts in accounts_by_provider.items():
        for acc in accounts:
            total_count += 1
            
            budget = acc.get("monthly_budget", 0)
            usage = acc.get("current_usage", 0)
            total_budget += budget
            total_usage += usage
            
            usage_pct = (usage / budget * 100) if budget > 0 else 0
            
            # Determine health status
            if usage_pct < 70:
                health = "🟢 Healthy"
                healthy_count += 1
            elif usage_pct < 85:
                health = "🟡 Warning"
            elif usage_pct < 95:
                health = "🟠 Critical"
            else:
                health = "🔴 Exhausted"
            
            enabled = "Enabled" if acc.get("enabled", False) else "Disabled"
            
            print(f"{acc['name']} ({provider_type})")
            print(f"  Status: {enabled} | Health: {health}")
            print(f"  Usage: ${usage:.2f}/${budget:.2f} ({usage_pct:.1f}%)\n")
    
    # Summary
    print("=" * 50)
    overall_pct = (total_usage / total_budget * 100) if total_budget > 0 else 0
    print(f"TOTAL: ${total_usage:.2f} / ${total_budget:.2f} ({overall_pct:.1f}%)")
    print(f"Accounts: {healthy_count}/{total_count} healthy\n")


def remove_account(account_id: str):
    """Remove an account by ID"""
    config = load_accounts()
    
    found = False
    for provider_type in config.get("accounts", {}):
        accounts = config["accounts"][provider_type]
        for i, acc in enumerate(accounts):
            if acc.get("id") == account_id:
                found = True
                confirm = input(f"Remove account '{account_id}'? (y/N): ").strip().lower()
                if confirm == 'y':
                    accounts.pop(i)
                    save_accounts(config)
                    print(f"✅ Account '{account_id}' removed")
                else:
                    print("Cancelled")
                break
        if found:
            break
    
    if not found:
        print(f"❌ Account '{account_id}' not found")


def manage_accounts(args):
    """Main entry point for accounts command"""
    if args.list:
        list_accounts()
    elif args.add:
        add_account_interactive()
    elif args.remove:
        remove_account(args.remove)
    elif args.status:
        show_account_status()
    else:
        print("Use --list, --add, --remove, or --status")
