import os

import click
import yaml
from pr_pilot.util import create_task, wait_for_result
from rich.console import Console
from rich.markdown import Markdown
from yaspin import yaspin

CONFIG_LOCATION = os.path.expanduser('~/.pr-pilot.yaml')
CONFIG_API_KEY = "api_key"


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
@click.option('--wait', is_flag=True, help='Wait for the result.')
@click.argument('repo')
@click.argument('prompt', nargs=-1)
def pilot_command(wait, repo, prompt):
    prompt = ' '.join(prompt)
    config = load_config()
    if not os.getenv("PR_PILOT_API_KEY"):
        os.environ["PR_PILOT_API_KEY"] = config[CONFIG_API_KEY]
    with yaspin(text="Creating new task", color="cyan") as sp:
        task = create_task(repo, prompt)
        dashboard_url = f"https://app.pr-pilot.ai/dashboard/tasks/{task.id}/"
        sp.write(f"✅ Task created: {dashboard_url}")
        if wait:
            sp.text = "Waiting for the result"
            try:
                result = wait_for_result(task)
                sp.ok("✅")
                console = Console()
                console.print(Markdown(result))
            except Exception as e:
                sp.fail("💥")
                click.echo(f"Error: {e}")
        else:
            click.echo(f"Task created: {dashboard_url}")


if __name__ == '__main__':
    pilot_command()