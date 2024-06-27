import functools
import os
import subprocess
from datetime import datetime, timezone

import click
import humanize
import yaml
from pr_pilot import Task
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from cli.constants import CONFIG_LOCATION, CONFIG_API_KEY


def clean_code_block_with_language_specifier(response):
    lines = response.split("\n")

    # Check if the first line starts with ``` followed by a language specifier
    # and the last line is just ```
    if lines[0].startswith("```") and lines[-1].strip() == "```":
        # Remove the first and last lines
        cleaned_lines = lines[1:-1]
    else:
        cleaned_lines = lines

    clean_response = "\n".join(cleaned_lines)
    return clean_response


def collect_user_preferences():
    console = Console()
    api_key_url = "https://app.pr-pilot.ai/dashboard/api-keys/"
    console.print(f"Please create an API key at {api_key_url}.")
    api_key = click.prompt("PR Pilot API key")

    console.line()
    console.print(
        "[green]Since it's the first time you're using PR Pilot, "
        "let's set some default values.[/green]"
    )
    console.line()
    auto_sync = click.confirm(
        "When a new PR/branch is created, do you want it checked out automatically?"
    )
    verbose = click.confirm("Do you want to see detailed status messages?")
    console.line()
    with open(CONFIG_LOCATION, "w") as f:
        f.write(
            yaml.dump(
                {
                    CONFIG_API_KEY: api_key,
                    "auto_sync": auto_sync,
                    "verbose": verbose,
                }
            )
        )
    console.print(f"Configuration saved in [code]{CONFIG_LOCATION}[/code]")


def load_config():
    """Load the configuration from the default location. If it doesn't exist,
    ask user to enter API key and save config."""
    console = Console()
    if not os.path.exists(CONFIG_LOCATION) and not os.getenv("PR_PILOT_API_KEY"):
        collect_user_preferences()

    if not os.path.exists(CONFIG_LOCATION) and os.getenv("PR_PILOT_API_KEY"):
        console.print(
            "[bold yellow]Using API key from environment variable PR_PILOT_API_KEY[/bold yellow]"
        )
        config = {CONFIG_API_KEY: os.getenv("PR_PILOT_API_KEY")}
    else:
        with open(CONFIG_LOCATION) as f:
            config = yaml.safe_load(f)

    return config


def pull_branch_changes(status_indicator, console, branch, debug=False):
    status_indicator.start()
    status_indicator.update(f"Pull latest changes from {branch}")
    error = ""
    try:
        # Fetch origin and checkout branch
        subprocess_params = dict(stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        subprocess.run(["git", "fetch", "origin"], **subprocess_params)
        subprocess.run(["git", "checkout", branch], **subprocess_params)
        # Capture output of git pull
        result = subprocess.run(["git", "pull", "origin", branch], **subprocess_params)
        output = result.stdout
        error = result.stderr
        status_indicator.success()
        if debug:
            console.line()
            console.print(output)
            console.line()
    except Exception as e:
        status_indicator.fail()
        console.print("[bold red]An error occurred:" f"[/bold red] {type(e)} {str(e)}\n\n{error}")
    finally:
        status_indicator.stop()


class TaskFormatter:

    def __init__(self, task: Task):
        self.task = task

    def format_github_project(self):
        return (
            f"[link=https://github.com/{self.task.github_project}]{self.task.github_project}[/link]"
        )

    def format_created_at(self):
        # If task was created less than 23 hours ago, show relative time
        now = datetime.now(timezone.utc)  # Use timezone-aware datetime
        if (now - self.task.created).days == 0:
            return humanize.naturaltime(self.task.created)
        local_time = self.task.created.astimezone()
        return local_time.strftime("%Y-%m-%d %H:%M:%S")

    def format_pr_link(self):
        if self.task.pr_number:
            return (
                f"[link=https://github.com/{self.task.github_project}/pull/"
                f"{self.task.pr_number}]#{self.task.pr_number}[/link]"
            )
        return ""

    def format_status(self):
        if self.task.status == "running":
            return f"[bold yellow]{self.task.status}[/bold yellow]"
        elif self.task.status == "completed":
            return f"[bold green]{self.task.status}[/bold green]"
        elif self.task.status == "failed":
            return f"[bold red]{self.task.status}[/bold red]"

    def format_title(self):
        dashboard_url = f"https://app.pr-pilot.ai/dashboard/tasks/{str(self.task.id)}/"
        return f"[link={dashboard_url}]{self.task.title}[/link]"

    def format_branch(self):
        return Markdown(f"`{self.task.branch}`")


def get_current_branch():
    return os.popen("git rev-parse --abbrev-ref HEAD").read().strip()


def is_branch_pushed(branch):
    return os.popen(f"git branch -r --list origin/{branch}").read().strip() != ""


def get_branch_if_pushed():
    current_branch = get_current_branch()
    if current_branch not in ["master", "main"] and is_branch_pushed(current_branch):
        return current_branch
    return None


def markdown_panel(title, content):
    """Create a Rich panel with markdown content that automatically fits the width"""
    # Calculate width based on the text content
    max_line_length = max(len(line) for line in content.split("\n"))
    padding = 4  # Adjust padding as necessary
    width = max_line_length + padding
    return Panel.fit(Markdown(content), title=title, width=width)


@functools.lru_cache()
def is_git_repo():
    """Check if the current directory is part of a Git repository."""
    try:
        subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return True
    except subprocess.CalledProcessError:
        return False


@functools.lru_cache()
def get_git_root():
    """Get the root directory of the current Git repository."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return result.stdout.decode("utf-8").strip()
    except subprocess.CalledProcessError:
        return None
