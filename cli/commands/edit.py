import os
from pathlib import Path

import click
from rich.console import Console

from cli.models import TaskParameters
from cli.status_indicator import StatusIndicator
from cli.task_runner import TaskRunner
from cli.util import pull_branch_changes


@click.command()
@click.option("--snap", is_flag=True, help="📸 Add a screenshot to your prompt.")
@click.argument("file_path", type=click.Path(exists=True))
@click.argument("prompt", required=False, default=None, type=str)
@click.pass_context
def edit(ctx, snap, file_path, prompt):
    """✍️ Let PR Pilot edit a file for you.

    Examples:

    \b
    - ✍️ Quickly add docstrings to a Python file:
      pilot edit main.py "Add docstrings for all classes, functions and parameters"

    \b
    - ♻️ Refactor and clean up code:
      pilot edit main.js "Break up large functions, organize the file and add comments"

    \b
    - 🧩 Implement placeholders:
      pilot edit "I left placeholder comments in the file. Please replace them with the actual code"

    """
    console = Console()
    status_indicator = StatusIndicator(
        spinner=ctx.obj["spinner"], messages=ctx.obj["verbose"], console=console
    )

    if not prompt:
        prompt = click.edit("", extension=".md")

    file_content = Path(file_path).read_text()
    user_prompt = prompt
    prompt = f"I have the following file content:\n\n---\n{file_content}\n---\n\n"
    prompt += f"Please edit the file content above in the following way:\n\n{user_prompt}"

    try:
        if ctx.obj["sync"] and not ctx.obj["branch"]:
            # Get current branch from git
            current_branch = os.popen("git rev-parse --abbrev-ref HEAD").read().strip()
            if current_branch not in ["master", "main"]:
                ctx.obj["branch"] = current_branch

        task_params = TaskParameters(
            snap=snap,
            wait=ctx.obj["wait"],
            repo=ctx.obj["repo"],
            verbose=ctx.obj["verbose"],
            output=file_path,
            code=True,
            model=ctx.obj["model"],
            debug=ctx.obj["debug"],
            prompt=prompt,
            branch=ctx.obj["branch"],
        )

        runner = TaskRunner(status_indicator)
        finished_task = runner.run_task(task_params)
        if ctx.obj["sync"]:
            pull_branch_changes(status_indicator, console, finished_task.branch, ctx.obj["debug"])

    except Exception as e:
        status_indicator.fail()
        raise click.ClickException(f"An error occurred: {type(e)} {str(e)}")

    finally:
        status_indicator.stop()
