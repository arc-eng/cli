import click
from rich.console import Console

from cli.plan_executor import PlanExecutor
from cli.status_indicator import StatusIndicator
from cli.util import pull_branch_changes


@click.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.pass_context
def plan(ctx, file_path):
    """📋 Let PR Pilot execute a plan for you.

    Learn more: https://docs.pr-pilot.ai/user_guide.html
    """
    console = Console()
    show_spinner = ctx.obj['spinner'] and not ctx.obj['quiet']
    status_indicator = StatusIndicator(spinner=show_spinner, messages=not ctx.obj['quiet'], console=console)

    try:
        runner = PlanExecutor(file_path, status_indicator)
        runner.run(ctx.obj['wait'], ctx.obj['repo'], ctx.obj['quiet'], ctx.obj['model'], ctx.obj['debug'])
        if ctx.obj['sync']:
            pull_branch_changes(status_indicator, console, ctx.obj['branch'], ctx.obj['debug'])

    except Exception as e:
        status_indicator.fail()
        if ctx.obj['debug']:
            raise e
        console.print(f"[bold red]An error occurred:[/bold red] {type(e)} {str(e)}")
    finally:
        status_indicator.stop()