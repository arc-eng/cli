import click

from cli.constants import CHEAP_MODEL, DEFAULT_MODEL
from cli.task_runner import TaskRunner


@click.command()
@click.option('--wait/--no-wait', is_flag=True, default=True, help='Wait for PR Pilot to finish the task.')
@click.option('--repo', help='Github repository in the format owner/repo.', required=False)
@click.option('--snap', is_flag=True, help='Select a portion of your screen to add as an image to the task.')
@click.option('--batch', '-b', type=click.Path(exists=True), help='Path to YAML file containing a list of tasks for PR Pilot.')
@click.option('--edit', '-e', type=click.Path(exists=True), help='Let PR Pilot edit a file for you.')
@click.option('--spinner/--no-spinner', is_flag=True, default=True, help='Display a loading indicator.')
@click.option('--quiet', is_flag=True, default=False, help='Disable all output on the terminal.')
@click.option('--cheap', is_flag=True, default=False, help=f'Use the cheapest GPT model ({CHEAP_MODEL})')
@click.option('--code', is_flag=True, default=False, help='Optimize prompt and settings for generating code')
@click.option('--file', '-f', type=click.Path(exists=True), help='Generate prompt from a template file.')
@click.option('--direct', is_flag=True, default=False,
              help='Do not feed the rendered template as a prompt into PR Pilot, but render it directly as output.')
@click.option('--output', '-o', type=click.Path(exists=False), help='Output file for the result.')
@click.option('--model', '-m', help='GPT model to use.', default=DEFAULT_MODEL)
@click.option('--debug', is_flag=True, default=False, help='Display debug information.')
@click.argument('prompt', nargs=-1)
def main(wait, repo, snap, batch, edit, spinner, quiet, cheap, code, file, direct, output, model, debug, prompt):
    """Create a new task for PR Pilot - https://docs.pr-pilot.ai"""
    runner = TaskRunner()
    runner.run_task(wait, repo, snap, edit, spinner, quiet, cheap, code, file, direct, output, model, debug, prompt)


if __name__ == '__main__':
    main()