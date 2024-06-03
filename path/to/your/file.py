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

CONFIG_LOCATION = os.path.expanduser('~/.pr-pilot.yaml')
CONFIG_API_KEY = "api_key"
CODE_MODEL = "gpt-4o"
CHEAP_MODEL = "gpt-3.5-turbo"
POLL_INTERVAL = 2
CODE_PRIMER = "ONLY respond with the code/content, no other text. Do not wrap it in triple backticks."
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
@click.option('--wait/--no-wait', is_flag=True, default=True, help='Wait for the result.')
@click.option('--repo', help='Github repository in the format owner/repo.', required=False)
@click.option('--snap', is_flag=True, help='Adds a part of your screen as an image to the task.')
@click.option('--edit', '-e', type=click.Path(exists=True), help='Let PR Pilot edit a file for you.')
@click.option('--spinner/--no-spinner', is_flag=True, default=True, help='Display a loading indicator')
@click.option('--quiet', is_flag=True, default=False, help='No pretty-print, no status indicator or messages.')
@click.option('--cheap', is_flag=True, default=False, help=f'Use the cheapest GPT model ({CHEAP_MODEL})')
@click.option('--code', is_flag=True, default=False, help='Optimize prompt and settings for generating code')
@click.option('--file', '-f', type=click.Path(exists=True), help='Load prompt from a template file.')
@click.option('--direct', is_flag=True, default=False,
              help='Do not feed the rendered template as a prompt into PR Pilot, but render it directly as output.')
@click.option('--output', '-o', type=click.Path(exists=False), help='Output file for the result.')
@click.option('--model', '-m', help='GPT model to use.', default=DEFAULT_MODEL)
@click.option('--debug', is_flag=True, default=False, help='Display debug information.')
@click.argument('prompt', nargs=-1)
def main(wait, repo, snap, edit, spinner, quiet, cheap, code, file, direct, output, model, debug, prompt):
    """Main function to handle the CLI commands and options."""
    prompt = ' '.join(prompt)
    config = load_config()
    console = Console()
    show_spinner = spinner and not quiet
    status = StatusIndicator(spinner=show_spinner, messages=not quiet, console=console)
    screenshot = take_screenshot() if snap else None

    if not os.getenv("PR_PILOT_API_KEY"):
        os.environ["PR_PILOT_API_KEY"] = config[CONFIG_API_KEY]
    if not repo:
        # No repository provided, try to detect it
        repo = detect_repository()
    if not repo:
        # Current directory is not a git repository, see if there is a default repo in the config
        repo = config.get("default_repo")
    if not repo:
        console.print(f"No Github repository provided. Use --repo or set 'default_repo' in {CONFIG_LOCATION}.")
        return
    if file:
        status.start()
        renderer = PromptTemplate(file, repo, model, status)
        prompt = renderer.render()
    if not prompt:
        prompt = click.edit("", extension=".md")
        if not prompt:
            console.print("No prompt provided.")
            return

    if edit:
        file_content = Path(edit).read_text()
        user_prompt = prompt
        prompt = f"I have the following file content:\n\n---\n{file_content}\n---\n\n"
        prompt += f"Please edit the file content above in the following way:\n\n{user_prompt}\n\n{CODE_PRIMER}"
        if not output:
            output = edit

    if cheap:
        model = CHEAP_MODEL
    if code:
        prompt += "\n\n" + CODE_PRIMER
        if not model:
            model = CODE_MODEL

    if direct:
        # Do not send the prompt, just return it as the result
        if output:
            with open(output, "w") as f:
                f.write(prompt)
            status.stop()
            if not quiet:
                console.line()
                console.print(Markdown(f"Rendered template `{file}` into `{output}`"))
                console.line()
            return
    status.start()
    status.update("Creating new task")
    task = create_task(repo, prompt, log=False, gpt_model=model, image=screenshot)
    status.update(f"Task created: https://app.pr-pilot.ai/dashboard/tasks/{task.id}")
    status.success()
    if debug:
        console.print(task)
    if wait:
        task_handler = TaskHandler(task, status)
        task_handler.wait_for_result(output, quiet)
    status.stop()
    if debug:
        console.print(task)


if __name__ == '__main__':
    main()