import os
import click
from rich.console import Console
from rich.padding import Padding

from cli.constants import CHEAP_MODEL
from cli.status_indicator import StatusIndicator
from cli.task_runner import TaskRunner
from cli.models import TaskParameters
from cli.util import pull_branch_changes
from cli.command_index import CommandIndex, Command


@click.command()
@click.option('--snap', is_flag=True, help='📸 Select a portion of your screen to add as an image to the task.')
@click.option('--cheap', is_flag=True, default=False, help=f'💸 Use the cheapest GPT model ({CHEAP_MODEL})')
@click.option('--code', is_flag=True, default=False, help='💻 Optimize prompt and settings for generating code')
@click.option('--file', '-f', type=click.Path(exists=True), help='📂 Generate prompt from a template file.')
@click.option('--direct', is_flag=True, default=False,
              help='🔄 Do not feed the rendered template as a prompt into PR Pilot, but render it directly as output.')
@click.option('--output', '-o', type=click.Path(exists=False), help='💾 Output file for the result.')
@click.option('--save-command', is_flag=True, help='💾 Save the task parameters as a command in pilot-commands.yaml')
@click.argument('prompt', required=False, default=None, type=str)
@click.pass_context
def task(ctx, snap, cheap, code, file, direct, output, save_command, prompt):
    """🛠️ Create a new task for PR Pilot.

    Examples:

    \b
    - Generate unit tests for a Python file:
      pilot task -o test_utils.py --code "Write some unit tests for the utils.py file."

    \b
    - Create a Bootstrap5 component based on a screenshot:
      pilot task -o component.html --code --snap "Write a Bootstrap5 component that looks like this."

    \b
    - Send a list of all bug issues to Slack:
      pilot task "Find all open Github issues labeled as 'bug' and send them to the #bugs Slack channel."
    """
    console = Console()
    status_indicator = StatusIndicator(spinner=ctx.obj['spinner'], messages=not ctx.obj['quiet'], console=console)

    try :
        if ctx.obj['sync']:
            # Get current branch from git
            current_branch = os.popen('git rev-parse --abbrev-ref HEAD').read().strip()
            if (current_branch not in ['master', 'main']):
                ctx.obj['branch'] = current_branch

        task_params = TaskParameters(
            wait=ctx.obj['wait'],
            repo=ctx.obj['repo'],
            snap=snap,
            quiet=ctx.obj['quiet'],
            cheap=cheap,
            code=code,
            file=file,
            direct=direct,
            output=output,
            model=ctx.obj['model'],
            debug=ctx.obj['debug'],
            prompt=prompt,
            branch=ctx.obj['branch']
        )

        runner = TaskRunner(status_indicator)
        finished_task = runner.run_task(task_params)

        if ctx.obj['sync']:
            branch = finished_task.branch if finished_task else ctx.obj['branch']
            if branch:
                pull_branch_changes(status_indicator, console, branch, ctx.obj['debug'])


        if save_command:
            command_index = CommandIndex()
            console.print(Padding("Save the task parameters as a command:", (1, 1)))
            name = click.prompt("  Name (e.g. generate-pr-desc)", type=str)
            description = click.prompt("  Short description", type=str)
            command = Command(name=name, description=description, params=task_params)
            command_index.add_command(command)
            console.print(Padding(f"Command saved to `{command_index.file_path}`:", (1, 1)))
            console.print(Padding(command.dict(), 1, 1))
            console.line()
            console.print(Padding(f"You can now run this command with `pilot run {name}`.", (1, 1)))


    except Exception as e:
        status_indicator.fail()
        if ctx.obj['debug']:
            raise
        console.print(f"[bold red]An error occurred:[/bold red] {type(e)} {str(e)}")
    finally:
        status_indicator.stop()
