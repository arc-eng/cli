import click
from rich.console import Console

from cli.plan_executor import PlanExecutor
from cli.status_indicator import StatusIndicator
from cli.util import pull_branch_changes, get_branch_if_pushed


@click.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.pass_context
def plan(ctx, file_path):
    """📋 Let PR Pilot execute a plan for you.

    Learn more: https://docs.pr-pilot.ai/user_guide.html
    """
    console = Console()
    status_indicator = StatusIndicator(
        spinner=ctx.obj["spinner"], messages=ctx.obj["verbose"], console=console
    )
    if ctx.obj["sync"]:
        ctx.obj["branch"] = get_branch_if_pushed()

    runner = PlanExecutor(file_path, status_indicator)
    runner.run(
        ctx.obj["wait"],
        ctx.obj["repo"],
        ctx.obj["verbose"],
        ctx.obj["model"],
        ctx.obj["debug"],
    )
    if ctx.obj["sync"]:
        pull_branch_changes(status_indicator, console, ctx.obj["branch"], ctx.obj["debug"])
