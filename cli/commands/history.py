import os
import json
import click
from rich.console import Console

HISTORY_FILE = "history.json"

@click.group()
def history():
    """📜 Access the history of tasks."""
    pass

@history.command()
@click.argument('item', type=click.Choice(['prompt', 'result'], case_sensitive=False))
def last(item):
    """Show the last task's prompt or result."""
    console = Console()
    if not os.path.exists(HISTORY_FILE):
        console.print("[bold red]No history found.[/bold red]")
        return

    with open(HISTORY_FILE, 'r') as f:
        history = json.load(f)

    if not history:
        console.print("[bold red]No history found.[/bold red]")
        return

    last_task = history[-1]
    if item == 'prompt':
        console.print(f"[bold green]Last prompt:[/bold green] {last_task['prompt']}")
    elif item == 'result':
        console.print(f"[bold green]Last result:[/bold green] {last_task['result']}")
