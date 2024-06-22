import click
from pr_pilot.util import list_tasks
from rich.console import Console
from rich.markdown import Markdown
from rich.padding import Padding
from rich.table import Table

from cli.util import TaskFormatter, markdown_panel

NO_TASKS_MESSAGE = """
You have no tasks yet. Run a task with `pilot task` to create one.
"""


@click.group(invoke_without_command=True)
@click.pass_context
def history(ctx):
    """📜 Access recent tasks."""
    tasks = list_tasks()
    ctx.obj["tasks"] = tasks

    if ctx.invoked_subcommand is None:
        # Default behavior when no sub-command is invoked
        console = Console()
        if not tasks:
            console.print(Padding(Markdown(NO_TASKS_MESSAGE), (1, 1)))
            return
        task_number = 1

        table = Table(box=None)

        table.add_column("#", justify="left", style="bold yellow", no_wrap=True)
        table.add_column("Timestamp", justify="left", style="cyan", no_wrap=True)
        table.add_column("Project", justify="left", style="magenta", no_wrap=True)
        table.add_column("PR")
        table.add_column("Status")
        table.add_column("Title", style="blue")

        for task in tasks:
            task_formatter = TaskFormatter(task)
            table.add_row(
                str(task_number),
                task_formatter.format_created_at(),
                task_formatter.format_github_project(),
                task_formatter.format_pr_link(),
                task_formatter.format_status(),
                task_formatter.format_title(),
            )
            task_number += 1
        console.print(Padding(table, (1, 1)))
        return


@history.group(invoke_without_command=True)
@click.argument("task_number", required=False, type=int, default=1)
@click.pass_context
def last(ctx, task_number):
    """Show the n-th latest task. Default is the last task."""
    console = Console()
    tasks = ctx.obj["tasks"]
    if task_number > len(tasks):
        console.print(f"[bold red]There are less than {task_number} tasks.[/bold red]")
        raise click.Abort()
    ctx.obj["selected_task"] = tasks[task_number - 1]
    if ctx.invoked_subcommand is None:
        # Pretty print task properties using rich
        task = tasks[task_number - 1]
        # Print header using table grid
        table = Table(box=None, show_header=False)
        task_formatter = TaskFormatter(task)
        table.add_column("Property", justify="left", style="bold yellow", no_wrap=True)
        table.add_column("Value", justify="left", style="cyan")
        table.add_row("Title", task_formatter.format_title())
        table.add_row("Status", task_formatter.format_status())
        table.add_row("Created", task_formatter.format_created_at())
        table.add_row("Project", task_formatter.format_github_project())
        if task.pr_number:
            table.add_row("PR", task_formatter.format_pr_link())
        if task.branch:
            table.add_row("Branch", task_formatter.format_branch())
        console.print(Padding(table, (1, 1)))
        console.print(markdown_panel("Prompt", task.user_request))
        console.print(markdown_panel("Result", task.result))


@last.command()
@click.option(
    "--markdown",
    is_flag=True,
    default=False,
    help="Return the prompt in markdown format.",
)
@click.pass_context
def prompt(ctx, markdown):
    """Show the n-th latest task's prompt."""
    console = Console()
    task = ctx.obj["selected_task"]
    if markdown:
        console.print(task.user_request)
    else:
        console.print(Markdown(task.user_request))


@last.command()
@click.option(
    "--markdown",
    is_flag=True,
    default=False,
    help="Return the result in markdown format.",
)
@click.pass_context
def result(ctx, markdown):
    """Show the n-th latest task's result."""
    console = Console()
    task = ctx.obj["selected_task"]
    if markdown:
        console.print(task.result)
    else:
        console.print(Markdown(task.result))
