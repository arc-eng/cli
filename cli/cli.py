import os
from pathlib import Path

import click
import yaml
from pr_pilot.util import create_task
from rich.console import Console
from rich.markdown import Markdown

from cli.detect_repository import detect_repository
from cli.prompt_template import PromptTemplate
from cli.status_indicator import StatusIndicator
from cli.task_handler import TaskHandler
from cli.task_runner import TaskRunner

CONFIG_LOCATION = os.path.expanduser('~/.pr-pilot.yaml')
CONFIG_API_KEY = "api_key"
CODE_MODEL = "gpt-4o"
CHEAP_MODEL = "gpt-3.5-turbo"
POLL_INTERVAL = 2
CODE_PRIMER = "Do not write anything to file, but ONLY respond with the code/content, no other text. Do not wrap it in triple backticks."
DEFAULT_MODEL = "gpt-4o"


def load_config():
    """Load the configuration from the default location. If it doesn't exist,
    ask user to enter API key and save config."""
    if not os.path.exists(CONFIG_LOCATION):
        if os.getenv("PR_PILOT_API_KEY"):
            click.echo("Using API key from environment variable.")
            api_key = os.getenv("PR_PILOT_API_KEY")
        else:
            api_key_url = "https://app.pr-pilot.ai/dashboard/api-keys/"
            click.echo(f"Configuration file not found. Please create an API key at {api_key_url}.")
            api_key = click.prompt("PR Pilot API key")
        with open(CONFIG_LOCATION, "w") as f:
            f.write(f"{CONFIG_API_KEY}: {api_key}")
        click.echo(f"Configuration saved in {CONFIG_LOCATION}")
    with open(CONFIG_LOCATION) as f:
        config = yaml.safe_load(f)
    return config

def take_screenshot():
    """Take a screenshot of a portion of the screen."""
    screenshot_command = "screencapture -i /tmp/screenshot.png"
    os.system(screenshot_command)
    return Path("/tmp/screenshot.png")


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
    runner = TaskRunner(CONFIG_LOCATION, CONFIG_API_KEY, CODE_MODEL, CHEAP_MODEL, CODE_PRIMER, DEFAULT_MODEL)
    runner.run_task(wait, repo, snap, edit, spinner, quiet, cheap, code, file, direct, output, model, debug, prompt)


if __name__ == '__main__':
    main()