import click
from rich.console import Console
from rich.markdown import Markdown
from rich.padding import Padding

from cli.command_index import CommandIndex, PilotCommand
from cli.constants import CHEAP_MODEL
from cli.models import TaskParameters
from cli.status_indicator import StatusIndicator
from cli.task_runner import TaskRunner
from cli.util import pull_branch_changes, get_branch_if_pushed


@click.command()
@click.option(
    "--snap",
    is_flag=True,
    help="📸 Select a portion of your screen to add as an image to the task.",
)
@click.option(
    "--cheap",
    is_flag=True,
    default=False,
    help=f"💸 Use the cheapest GPT model ({CHEAP_MODEL})",
)
@click.option(
    "--code",
    is_flag=True,
    default=False,
    help="💻 Optimize prompt and settings for generating code",
)
@click.option(
    "--file",
    "-f",
    type=click.Path(exists=True),
    help="📂 Generate prompt from a template file.",
)
@click.option(
    "--direct",
    is_flag=True,
    default=False,
    help="🔄 Do not feed the rendered template as a prompt into PR Pilot, "
    "but render it directly as output.",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(exists=False),
    help="💾 Output file for the result.",
)
@click.option(
    "--save-command",
    is_flag=True,
    help="💾 Save the task parameters as a command for later use.",
)
@click.argument("prompt", required=False, default=None, type=str)
@click.pass_context
def task(ctx, snap, cheap, code, file, direct, output, save_command, prompt):
    """➕ Create a new task for PR Pilot.

    Examples: https://github.com/pr-pilot-ai/pr-pilot-cli
    """
    console = Console()
    status_indicator = StatusIndicator(
        spinner=ctx.obj["spinner"], messages=ctx.obj["verbose"], console=console
    )

    try:
        if ctx.obj["sync"]:
            ctx.obj["branch"] = get_branch_if_pushed()

        task_params = TaskParameters(
            wait=ctx.obj["wait"],
            repo=ctx.obj["repo"],
            snap=snap,
            verbose=ctx.obj["verbose"],
            cheap=cheap,
            code=code,
            file=file,
            direct=direct,
            output=output,
            model=ctx.obj["model"],
            debug=ctx.obj["debug"],
            prompt=prompt,
            branch=ctx.obj["branch"],
            spinner=ctx.obj["spinner"],
            sync=ctx.obj["sync"],
        )

        if save_command:
            command_index = CommandIndex()
            console.print(
                Padding(
                    "[green bold]Save the task parameters as a command:[/green bold]",
                    (1, 1),
                )
            )
            name = click.prompt("  Name (e.g. generate-pr-desc)", type=str)
            description = click.prompt("  Short description", type=str)
            command = PilotCommand(name=name, description=description, params=task_params)
            command_index.add_command(command)
            console.print(
                Padding(f"Command saved to [code]{command_index.file_path}[/code]", (1, 1))
            )
            console.print(
                Padding(
                    Markdown(f"You can now run this command with `pilot run {name}`."),
                    (1, 1),
                )
            )
            return

        runner = TaskRunner(status_indicator)
        finished_task = runner.run_task(task_params)

        if ctx.obj["sync"]:
            branch = finished_task.branch if finished_task else ctx.obj["branch"]
            if branch:
                pull_branch_changes(status_indicator, console, branch, ctx.obj["debug"])

    finally:
        status_indicator.stop()
