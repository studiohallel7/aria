"""
CLI Entry Point for Autonomous Agent
Usage: python -m cmd.agent_cli.main [command] [options]
"""

import argparse
import sys
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(
        description="Autonomous AI Agent CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s run                    # Start agent in continuous mode
  %(prog)s run --mode free        # Start in free exploration mode
  %(prog)s add "analyze code"     # Add a task to the queue
  %(prog)s status                 # Show current agent status
  %(prog)s logs                   # View recent logs
  %(prog)s config                 # Show/edit configuration
  %(prog)s memory                 # Manage agent memory
  %(prog)s accounts               # Manage API accounts
  %(prog)s providers              # Manage LLM providers
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Run command
    run_parser = subparsers.add_parser("run", help="Start the agent")
    run_parser.add_argument(
        "--mode", 
        choices=["work", "free"], 
        default="work",
        help="Agent mode: work (follows user) or free (autonomous)"
    )
    run_parser.add_argument(
        "--interval", 
        type=int, 
        default=5,
        help="Base loop interval in seconds"
    )
    run_parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate without executing actions"
    )
    
    # Add task command
    add_parser = subparsers.add_parser("add", help="Add a task to the queue")
    add_parser.add_argument("task", help="Task description")
    add_parser.add_argument(
        "--priority",
        type=int,
        choices=[1, 2, 3],
        default=2,
        help="Task priority (1=high, 2=normal, 3=low)"
    )
    add_parser.add_argument(
        "--urgent",
        action="store_true",
        help="Mark task as urgent"
    )
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Show agent status")
    status_parser.add_argument(
        "--json",
        action="store_true",
        help="Output in JSON format"
    )
    
    # Logs command
    logs_parser = subparsers.add_parser("logs", help="View logs")
    logs_parser.add_argument(
        "--lines", "-n",
        type=int,
        default=50,
        help="Number of lines to show"
    )
    logs_parser.add_argument(
        "--level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Filter by log level"
    )
    logs_parser.add_argument(
        "--follow", "-f",
        action="store_true",
        help="Follow logs in real-time"
    )
    
    # Config command
    config_parser = subparsers.add_parser("config", help="Manage configuration")
    config_parser.add_argument(
        "--edit",
        action="store_true",
        help="Open config file in editor"
    )
    config_parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate configuration files"
    )
    config_parser.add_argument(
        "--section",
        choices=["agent", "providers", "accounts", "safety"],
        help="Show specific configuration section"
    )
    
    # Memory command
    memory_parser = subparsers.add_parser("memory", help="Manage agent memory")
    memory_parser.add_argument(
        "--list",
        action="store_true",
        help="List memory entries"
    )
    memory_parser.add_argument(
        "--search",
        type=str,
        help="Search memory"
    )
    memory_parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear all memory"
    )
    memory_parser.add_argument(
        "--export",
        type=str,
        help="Export memory to file"
    )
    
    # Accounts command
    accounts_parser = subparsers.add_parser("accounts", help="Manage API accounts")
    accounts_parser.add_argument(
        "--list",
        action="store_true",
        help="List all accounts"
    )
    accounts_parser.add_argument(
        "--add",
        action="store_true",
        help="Add new account interactively"
    )
    accounts_parser.add_argument(
        "--remove",
        type=str,
        help="Remove account by ID"
    )
    accounts_parser.add_argument(
        "--status",
        action="store_true",
        help="Show account usage and health"
    )
    
    # Providers command
    providers_parser = subparsers.add_parser("providers", help="Manage LLM providers")
    providers_parser.add_argument(
        "--list",
        action="store_true",
        help="List all providers and models"
    )
    providers_parser.add_argument(
        "--add",
        action="store_true",
        help="Add new provider interactively"
    )
    providers_parser.add_argument(
        "--test",
        type=str,
        help="Test a specific model"
    )
    providers_parser.add_argument(
        "--compare",
        nargs="+",
        help="Compare multiple models"
    )
    
    # Health command
    health_parser = subparsers.add_parser("health", help="System health check")
    health_parser.add_argument(
        "--full",
        action="store_true",
        help="Run full diagnostic"
    )
    
    # Version command
    subparsers.add_parser("version", help="Show version")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(0)
    
    # Import and delegate to command handlers
    if args.command == "run":
        from cmd.agent_cli.run_cmd import run_agent
        run_agent(args)
    elif args.command == "add":
        from cmd.agent_cli.add_cmd import add_task
        add_task(args)
    elif args.command == "status":
        from cmd.agent_cli.status_cmd import show_status
        show_status(args)
    elif args.command == "logs":
        from cmd.agent_cli.logs_cmd import view_logs
        view_logs(args)
    elif args.command == "config":
        from cmd.agent_cli.config_cmd import manage_config
        manage_config(args)
    elif args.command == "memory":
        from cmd.agent_cli.memory_cmd import manage_memory
        manage_memory(args)
    elif args.command == "accounts":
        from cmd.agent_cli.accounts_cmd import manage_accounts
        manage_accounts(args)
    elif args.command == "providers":
        from cmd.agent_cli.providers_cmd import manage_providers
        manage_providers(args)
    elif args.command == "health":
        from cmd.agent_cli.health_cmd import check_health
        check_health(args)
    elif args.command == "version":
        from cmd.agent_cli.version_cmd import show_version
        show_version()
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
