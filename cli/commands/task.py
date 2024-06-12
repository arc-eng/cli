import os

import click
from rich.console import Console

from cli.constants import CHEAP_MODEL
from cli.status_indicator import StatusIndicator
from cli.task_runner import TaskRunner
from cli.util import pull_branch_changes


@click.command()
@click.option('--snap', is_flag=True, help='📸 Select a portion of your screen to add as an image to the task.')
@click.option('--cheap', is_flag=True, default=False, help=f'💸 Use the cheapest GPT model ({CHEAP_MODEL})')
@click.option('--code', is_flag=True, default=False, help='💻 Optimize prompt and settings for generating code')
@click.option('--file', '-f', type=click.Path(exists=True), help='📂 Generate prompt from a template file.')
@click.option('--direct', is_flag=True, default=False,
              help='🔄 Do not feed the rendered template as a prompt into PR Pilot, but render it directly as output.')
@click.option('--output', '-o', type=click.Path(exists=False), help='💾 Output file for the result.')
@click.argument('prompt', nargs=-1)
@click.pass_context
def task(ctx, snap, cheap, code, file, direct, output, prompt):
    """🛠️Create a new task for PR Pilot.

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
    show_spinner = ctx.obj['spinner'] and not ctx.obj['quiet']
    status_indicator = StatusIndicator(spinner=show_spinner, messages=not ctx.obj['quiet'], console=console)

    try:
        if ctx.obj['sync'] and not ctx.obj['branch']:
            # Get current branch from git
            ctx.obj['branch'] = os.popen('git rev-parse --abbrev-ref HEAD').read().strip()

        runner = TaskRunner(status_indicator)
        runner.run_task(ctx.obj['wait'], ctx.obj['repo'], snap, None, ctx.obj['quiet'], cheap, code, file, direct, output, ctx.obj['model'], ctx.obj['debug'], prompt, branch=ctx.obj['branch'])
        if ctx.obj['sync']:
            pull_branch_changes(status_indicator, console, ctx.obj['branch'], ctx.obj['debug'])

    except Exception as e:
        status_indicator.fail()
        console.print(f"[bold red]An error occurred:[/bold red] {type(e)} {str(e)}")
    finally:
        status_indicator.stop()