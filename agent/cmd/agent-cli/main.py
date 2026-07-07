"""
Autonomous Agent CLI - Main entry point.
"""

import sys
import os
import time
import signal
from datetime import datetime
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import click
from rich.console import Console
from rich.panel import Panel
from rich.status import Status

from core.state.agent_state import (
    AgentStatus, 
    AgentState, 
    OperationMode,
    get_current_state,
    save_current_state,
    get_context_manager,
    save_context_manager,
)
from infra.llm.client import get_client, LLMMessage
from infra.llm.providers.openai import OpenAIProvider
from infra.llm.providers.openrouter import OpenRouterProvider
from core.loop.main_loop import AgentLoop


console = Console()


def print_banner():
    """Print the agent banner."""
    banner = """
╔═══════════════════════════════════════════════════════════╗
║           AUTONOMOUS AGENT v0.1.0                         ║
║   Agente de IA Autônomo Single-Core                       ║
╚═══════════════════════════════════════════════════════════╝
    """
    console.print(Panel(banner, style="bold blue"))


def setup_providers():
    """Setup LLM providers."""
    client = get_client()
    
    try:
        openai_provider = OpenAIProvider()
        client.register_provider(openai_provider)
        console.print("[green]✓ OpenAI provider initialized[/green]")
    except Exception as e:
        console.print(f"[yellow]⚠ OpenAI provider not available: {e}[/yellow]")
    
    try:
        openrouter_provider = OpenRouterProvider()
        client.register_provider(openrouter_provider)
        console.print("[green]✓ OpenRouter provider initialized[/green]")
    except Exception as e:
        console.print(f"[yellow]⚠ OpenRouter provider not available: {e}[/yellow]")
    
    return client


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """Autonomous Agent CLI - Controle e monitore seu agente de IA."""
    pass


@cli.command()
@click.option("--mode", "-m", default="trabalho", type=click.Choice(["trabalho", "livre"]))
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
def run(mode: str, verbose: bool):
    """Iniciar o agente em modo contínuo."""
    print_banner()
    
    # Setup
    console.print("\n[bold]Inicializando agentes...[/bold]\n")
    setup_providers()
    
    # Load state
    state = get_current_state()
    state.mode = OperationMode(mode)
    state.state = AgentState.IDLE
    save_current_state(state)
    
    console.print(f"\n[bold cyan]Modo:[/bold cyan] {mode}")
    console.print(f"[bold cyan]Estado inicial:[/bold cyan] {state.state.value}")
    
    # Create and run loop
    loop = AgentLoop(verbose=verbose)
    
    # Handle interrupts
    def signal_handler(sig, frame):
        console.print("\n\n[yellow]Interrompendo agente...[/yellow]")
        state = get_current_state()
        state.state = AgentState.IDLE
        save_current_state(state)
        console.print("[green]Agente salvo. Até logo![/green]")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Run main loop
    console.print("\n[bold green]🚀 Iniciando loop principal...[/bold green]\n")
    loop.run()


@cli.command()
def status():
    """Mostrar status atual do agente."""
    print_banner()
    
    state = get_current_state()
    ctx = get_context_manager()
    
    console.print("\n[bold]Status do Agente[/bold]\n")
    console.print(f"  Estado: [cyan]{state.state.value}[/cyan]")
    console.print(f"  Modo: [cyan]{state.mode.value}[/cyan]")
    console.print(f"  Ciclo: [cyan]{state.cycle_count}[/cyan]")
    console.print(f"  Tarefa atual: [cyan]{state.current_task or 'Nenhuma'}[/cyan]")
    console.print(f"  Erros: [cyan]{state.error_count}[/cyan]")
    
    if state.last_cycle_time:
        console.print(f"  Último ciclo: [cyan]{state.last_cycle_time.strftime('%Y-%m-%d %H:%M:%S')}[/cyan]")
    
    pending_tasks = ctx.get_pending_tasks()
    if pending_tasks:
        console.print(f"\n[bold]Tarefas Pendentes ({len(pending_tasks)})[/bold]")
        for i, task in enumerate(pending_tasks[:5], 1):
            console.print(f"  {i}. {task['task']}")


@cli.command()
@click.argument("task")
@click.option("--priority", "-p", default=5, type=click.IntRange(1, 10))
def add(task: str, priority: int):
    """Adicionar uma tarefa para o agente executar."""
    ctx = get_context_manager()
    ctx.add_user_task(task, priority=priority)
    save_context_manager(ctx)
    
    console.print(f"\n[green]✓ Tarefa adicionada com prioridade {priority}[/green]")
    console.print(f"  '{task}'")


@cli.command()
def clear():
    """Limpar estado e contexto do agente."""
    state = AgentStatus()
    save_current_state(state)
    
    ctx = get_context_manager()
    ctx.items = []
    ctx.user_tasks = []
    save_context_manager(ctx)
    
    console.print("[green]✓ Estado limpo com sucesso[/green]")


@cli.command()
@click.option("--all", "-a", is_flag=True, help="Show all logs including debug")
def logs(all: bool):
    """Mostrar logs recentes do agente."""
    log_path = "./data/agent/logs"
    
    if not os.path.exists(log_path):
        console.print("[yellow]Nenhum log encontrado[/yellow]")
        return
    
    log_files = sorted(os.listdir(log_path), reverse=True)[:5]
    
    if not log_files:
        console.print("[yellow]Nenhum log encontrado[/yellow]")
        return
    
    console.print(f"\n[bold]Últimos logs ({len(log_files)} arquivos)[/bold]\n")
    
    for log_file in log_files:
        console.print(f"  📄 {log_file}")


if __name__ == "__main__":
    cli()