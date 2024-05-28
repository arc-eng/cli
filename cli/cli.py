import os

import click
import yaml
from pr_pilot.util import create_task, wait_for_result
from rich.console import Console
from rich.markdown import Markdown
from yaspin import yaspin

from cli.detect_repository import detect_repository

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
@click.option('--wait/--no-wait', is_flag=True, default=True, help='Wait for the result.')
@click.option('--repo', help='Github repository in the format owner/repo.', required=False)
@click.option('--chatty', is_flag=True, default=False, help='Print more information.')
@click.option('--raw', is_flag=True, default=False, help='For piping. No pretty-print, no status indicator.')
@click.argument('prompt', nargs=-1)
def main(wait, repo, chatty, raw, prompt):
    prompt = ' '.join(prompt)
    config = load_config()
    if not os.getenv("PR_PILOT_API_KEY"):
        os.environ["PR_PILOT_API_KEY"] = config[CONFIG_API_KEY]
    if not repo:
        # No repository provided, try to detect it
        repo = detect_repository()
    if not repo:
        # Current directory is not a git repository, see if there is a default repo in the config
        repo = config.get("default_repo")
    if not repo:
        click.echo(f"No Github repository provided. Use --repo or set 'default_repo' in {CONFIG_LOCATION}.")
        return
    if not prompt:
        click.echo("Please provide a prompt.")
        return

    if raw:
        task = create_task(repo, prompt, log=False)
        result = wait_for_result(task, log=False)
        print(result)
        return
    with yaspin(text=f"Creating new task for repository {repo}", color="cyan") as sp:
        task = create_task(repo, prompt)
        dashboard_url = f"https://app.pr-pilot.ai/dashboard/tasks/{task.id}/"
        if chatty:
            sp.write(f"✅ Task created: {dashboard_url}")
        if wait:
            sp.text = f"I'm working on it :) Track my progress in the dashboard: {dashboard_url}"
            try:
                result = wait_for_result(task)
                if chatty:
                    sp.ok("✅")
                else:
                    sp.hide()
                console = Console()
                console.line()
                if raw:
                    console.print(result)
                else:
                    console.print(Markdown(result))
            except Exception as e:
                sp.fail("💥")
                click.echo(f"Error: {e}")

if __name__ == '__main__':
    main()