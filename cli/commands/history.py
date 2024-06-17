import click
from pr_pilot.util import list_tasks
from rich.console import Console
from rich.markdown import Markdown
from rich.table import Table


@click.group(invoke_without_command=True)
@click.pass_context
def history(ctx):
    """📜 Access recent tasks."""
    tasks = list_tasks()
    ctx.obj['tasks'] = tasks

    if ctx.invoked_subcommand is None:
        # Default behavior when no sub-command is invoked
        console = Console()
        if not tasks:
            console.print("[bold red]No tasks found.[/bold red]")
        task_number = 1
        console.line()

        table = Table(box=None)

        table.add_column("#", justify="left", style="bold yellow", no_wrap=True)
        table.add_column("Timestamp", justify="left", style="cyan", no_wrap=True)
        table.add_column("Project", justify="left", style="magenta", no_wrap=True)
        table.add_column("PR")
        table.add_column("Status")
        table.add_column("Title", style="blue")

        for task in tasks:
            # Get date and time as yyyy-mm-dd hh:mm:ss from task.created
            created = task.created.strftime("%Y-%m-%d %H:%M:%S")
            status = task.status
            if task.status == "running":
                status = f"[bold yellow]{task.status}[/bold yellow]"
            elif task.status == "completed":
                status = f"[bold green]{task.status}[/bold green]"
            elif task.status == "failed":
                status = f"[bold red]{task.status}[/bold red]"
            dashboard_url = f"https://app.pr-pilot.ai/dashboard/tasks/{str(task.id)}/"
            linked_title = f"[link={dashboard_url}]{task.title}[/link]"
            project_link = f"[link=https://github.com/{task.github_project}]{task.github_project}[/link]"
            if task.pr_number:
                pr_link = f"[link=https://github.com/{task.github_project}/pull/{task.pr_number}]#{task.pr_number}[/link]"
            else:
                pr_link = ""
            table.add_row(str(task_number), created, project_link, pr_link, status, linked_title)
            task_number += 1
        console.print(table)
        console.line()
        return


@history.group(invoke_without_command=True)
@click.argument('task_number', required=False, type=int, default=1)
@click.pass_context
def last(ctx, task_number):
    """Show the last task."""
    console = Console()
    tasks = ctx.obj['tasks']
    if ctx.invoked_subcommand is None:
        console.print(tasks[-1])


@last.command()
@click.pass_context
def prompt(ctx):
    """Show the last task's prompt."""
    console = Console()
    tasks = ctx.obj['tasks']
    last_task = tasks[-1]
    console.print(Markdown(last_task.user_request))

@last.command()
@click.pass_context
def result(ctx):
    """Show the last task's result."""
    console = Console()
    tasks = ctx.obj['tasks']
    last_task = tasks[-1]
    console.print(Markdown(last_task.result))