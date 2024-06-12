import os

import click
from rich.console import Console

from cli.status_indicator import StatusIndicator
from cli.task_runner import TaskRunner
from cli.util import pull_branch_changes


@click.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.argument('prompt')
@click.pass_context
def edit(ctx, file_path, prompt):
    """✍️ Let PR Pilot edit a file for you.

    Examples:

    \b
    - ✍️ Quickly add docstrings to a Python file:
      pilot edit main.py "Add docstrings for all classes, functions and parameters."

    \b
    - ♻️ Refactor and clean up code:
      pilot edit main.js "Break up large functions, organize the file and add comments."

    \b
    - 🧩 Implement placeholders:
      pilot edit "I left placeholder comments in the file. Please replace them with the actual code."

    """
    console = Console()
    show_spinner = ctx.obj['spinner'] and not ctx.obj['quiet']
    status_indicator = StatusIndicator(spinner=show_spinner, messages=not ctx.obj['quiet'], console=console)

    try:
        if ctx.obj['sync'] and not ctx.obj['branch']:
            # Get current branch from git
            ctx.obj['branch'] = os.popen('git rev-parse --abbrev-ref HEAD').read().strip()

        runner = TaskRunner(status_indicator)
        runner.run_task(ctx.obj['wait'], ctx.obj['repo'], None, file_path, ctx.obj['quiet'], False, False, None, False, None, ctx.obj['model'], ctx.obj['debug'], prompt, branch=ctx.obj['branch'])
        if ctx.obj['sync']:
            pull_branch_changes(status_indicator, console, ctx.obj['branch'], ctx.obj['debug'])

    except Exception as e:
        status_indicator.fail()
        console.print(f"[bold red]An error occurred:[/bold red] {type(e)} {str(e)}")
    finally:
        status_indicator.stop()