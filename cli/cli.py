import os

import click
import yaml
from pr_pilot.util import create_task, wait_for_result, get_task
from rich.console import Console
from rich.markdown import Markdown
from yaspin import yaspin

from cli.detect_repository import detect_repository
from cli.task_handler import TaskHandler
from cli.prompt_template import PromptTemplate

CONFIG_LOCATION = os.path.expanduser('~/.pr-pilot.yaml')
CONFIG_API_KEY = "api_key"
CODE_MODEL = "gpt-4"
POLL_INTERVAL = 2


def load_config():
    """Load the configuration from the default location. If it doesn't exist,
    ask user to enter API key and save config."""
    if not os.path.exists(CONFIG_LOCATION):
        api_key_url = "https://app.pr-pilot.ai/dashboard/api-keys/"
        click.echo(f"Configuration file not found. Please create an API key at {api_key_url}.")
        api_key = click.prompt("PR Pilot API key")
        with open(CONFIG_LOCATION, "w") as f:
            f.write(f"{CONFIG_API_KEY}: {api_key}")
        click.echo(f"Configuration saved in {CONFIG_LOCATION}")
    with open(CONFIG_LOCATION) as f:
        config = yaml.safe_load(f)
    return config


@click.command()
@click.option('--wait/--no-wait', is_flag=True, default=True, help='Wait for the result.')
@click.option('--repo', help='Github repository in the format owner/repo.', required=False)
@click.option('--chatty', is_flag=True, default=False, help='Print more information.')
@click.option('--raw', is_flag=True, default=False, help='For piping. No pretty-print, no status indicator.')
@click.option('--code', is_flag=True, default=False, help='Disable formatting, enable RAW mode, use GPT-4 model.')
@click.option('--file', '-f', type=click.Path(exists=True), help='Load prompt from a template file.')
@click.option('--direct', is_flag=True, default=False,
              help='Do not use the rendered template as a prompt for PR Pilot, but render it directly as output.')
@click.option('--output', '-o', type=click.Path(exists=False), help='Output file for the result.')
@click.option('--model', help='GPT model to use.', default='gpt-4-turbo')
@click.option('--debug', is_flag=True, default=False, help='Display debug information.')
@click.argument('prompt', nargs=-1)
def main(wait, repo, chatty, raw, code, file, direct, output, model, debug, prompt):
    prompt = ' '.join(prompt)
    config = load_config()
    console = Console()

    if debug:
        chatty = True
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
        renderer = PromptTemplate(file, repo, model)
        prompt = renderer.render(show_spinner=not raw)
    if not prompt:
        prompt = click.edit("", extension=".md")
        if not prompt:
            console.print("No prompt provided.")
            return
    if code:
        raw = True
        prompt += "\n\nONLY respond with the code, no other text. Do not wrap it in triple backticks."
        model = CODE_MODEL

    if direct:
        # Do not send the prompt, just return it as the result
        if output:
            with open(output, "w") as f:
                f.write(prompt)
            console.print(Markdown(f"Rendered template `{file}` into `{output}`"))
            return

    task = create_task(repo, prompt, log=False, gpt_model=model)

    if not wait:
        if chatty:
            console.print(f"✅ Task created: https://app.pr-pilot.ai/dashboard/tasks/{task.id}")
        return

    task_handler = TaskHandler(task, show_spinner=not raw)
    task_handler.wait_for_result(output, raw)


if __name__ == '__main__':
    main()