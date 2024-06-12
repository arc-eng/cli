import os
import subprocess

import click
from rich.console import Console

from cli.plan_executor import PlanExecutor
from cli.constants import CHEAP_MODEL, DEFAULT_MODEL
from cli.status_indicator import StatusIndicator
from cli.task_runner import TaskRunner
from cli.util import pull_branch_changes


@click.group()
@click.option('--wait/--no-wait', is_flag=True, default=True, help='Wait for PR Pilot to finish the task.')
@click.option('--repo', help='Github repository in the format owner/repo.', required=False)
@click.option('--spinner/--no-spinner', is_flag=True, default=True, help='Display a loading indicator.')
@click.option('--quiet', is_flag=True, default=False, help='Disable all output on the terminal.')
@click.option('--model', '-m', help='GPT model to use.', default=DEFAULT_MODEL)
@click.option('--branch', '-b', help='Run the task on a specific branch.', required=False, default=None)
@click.option('--sync', is_flag=True, default=False, help='Run task on your current branch and pull PR Pilot\'s changes when done.')
@click.option('--debug', is_flag=True, default=False, help='Display debug information.')
@click.pass_context
def main(ctx, wait, repo, spinner, quiet, model, branch, sync, debug):
    """PR Pilot CLI - https://docs.pr-pilot.ai"""
    ctx.ensure_object(dict)
    ctx.obj['wait'] = wait
    ctx.obj['repo'] = repo
    ctx.obj['spinner'] = spinner
    ctx.obj['quiet'] = quiet
    ctx.obj['model'] = model
    ctx.obj['branch'] = branch
    ctx.obj['sync'] = sync
    ctx.obj['debug'] = debug


@click.command()
@click.option('--snap', is_flag=True, help='Select a portion of your screen to add as an image to the task.')
@click.option('--cheap', is_flag=True, default=False, help=f'Use the cheapest GPT model ({CHEAP_MODEL})')
@click.option('--code', is_flag=True, default=False, help='Optimize prompt and settings for generating code')
@click.option('--file', '-f', type=click.Path(exists=True), help='Generate prompt from a template file.')
@click.option('--direct', is_flag=True, default=False,
              help='Do not feed the rendered template as a prompt into PR Pilot, but render it directly as output.')
@click.option('--output', '-o', type=click.Path(exists=False), help='Output file for the result.')
@click.argument('prompt', nargs=-1)
@click.pass_context
def task(ctx, snap, cheap, code, file, direct, output, prompt):
    """Create a new task for PR Pilot"""
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


@click.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.argument('prompt')
@click.pass_context
def edit(ctx, file_path, prompt):
    """Let PR Pilot edit a file for you."""
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


@click.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.pass_context
def plan(ctx, file_path):
    """Let PR Pilot execute a plan for you."""
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
        console.print(f"[bold red]An error occurred:[/bold red] {type(e)} {str(e)}")
    finally:
        status_indicator.stop()


main.add_command(task)
main.add_command(edit)
main.add_command(plan)


if __name__ == '__main__':
    main()