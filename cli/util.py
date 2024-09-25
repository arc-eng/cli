import functools
import os
import subprocess
from datetime import datetime, timezone

import humanize
from arcane import Task
from rich import box
from rich.markdown import Markdown
from rich.panel import Panel


def clean_code_block_with_language_specifier(response):
    """
    Clean the code block by removing the language specifier and the enclosing backticks.

    Args:
        response (str): The response containing the code block.

    Returns:
        str: The cleaned code block.
    """
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


def pull_branch_changes(status_indicator, console, branch, debug=False):
    """
    Pull the latest changes from the specified branch.

    Args:
        status_indicator: The status indicator object.
        console: The console object for printing messages.
        branch (str): The branch to pull changes from.
        debug (bool, optional): If True, print debug information. Defaults to False.
    """
    status_indicator.start()
    status_indicator.update_spinner_message(f"Pulling changes from branch: {branch}")
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
        if debug:
            console.line()
            console.print(output)
            console.line()
        status_indicator.update_spinner_message("")
        status_indicator.log_message(
            f"Pull latest changes from `{branch}`", dim_text=True, character="↻"
        )
    except Exception as e:
        status_indicator.fail()
        console.print("[bold red]An error occurred:" f"[/bold red] {type(e)} {str(e)}\n\n{error}")
    finally:
        status_indicator.stop()


class TaskFormatter:
    """
    A class to format task information for display.

    Attributes:
        task (Task): The task object to format.
    """

    def __init__(self, task: Task):
        """
        Initialize the TaskFormatter with a task.

        Args:
            task (Task): The task object to format.
        """
        self.task = task

    def format_github_project(self):
        """
        Format the GitHub project link.

        Returns:
            str: The formatted GitHub project link.
        """
        return (
            f"[link=https://github.com/{self.task.github_project}]{self.task.github_project}[/link]"
        )

    def format_created_at(self):
        """
        Format the creation time of the task.

        Returns:
            str: The formatted creation time.
        """
        # If task was created less than 23 hours ago, show relative time
        now = datetime.now(timezone.utc)  # Use timezone-aware datetime
        if (now - self.task.created).days == 0:
            return humanize.naturaltime(self.task.created)
        local_time = self.task.created.astimezone()
        return local_time.strftime("%Y-%m-%d %H:%M:%S")

    def format_pr_link(self):
        """
        Format the pull request link.

        Returns:
            str: The formatted pull request link.
        """
        if self.task.pr_number:
            return (
                f"[link=https://github.com/{self.task.github_project}/pull/"
                f"{self.task.pr_number}]#{self.task.pr_number}[/link]"
            )
        return ""

    def format_status(self):
        """
        Format the status of the task.

        Returns:
            str: The formatted status.
        """
        if self.task.status == "running":
            return f"[bold yellow]{self.task.status}[/bold yellow]"
        elif self.task.status == "completed":
            return f"[bold green]{self.task.status}[/bold green]"
        elif self.task.status == "failed":
            return f"[bold red]{self.task.status}[/bold red]"

    def format_title(self):
        """
        Format the title of the task.

        Returns:
            str: The formatted title.
        """
        task_title = self.task.title.replace("\n", " ")[0:80]
        dashboard_url = f"https://arcane.engineer/dashboard/tasks/{str(self.task.id)}/"
        return f"[link={dashboard_url}]{task_title}[/link]"

    def format_branch(self):
        """
        Format the branch name.

        Returns:
            str: The formatted branch name.
        """
        return Markdown(f"`{self.task.branch}`")


def get_current_branch():
    """
    Get the current Git branch.

    Returns:
        str: The name of the current branch.
    """
    return os.popen("git rev-parse --abbrev-ref HEAD").read().strip()


def is_branch_pushed(branch):
    """
    Check if the branch is pushed to the remote repository.

    Args:
        branch (str): The branch name to check.

    Returns:
        bool: True if the branch is pushed, False otherwise.
    """
    return os.popen(f"git branch -r --list origin/{branch}").read().strip() != ""


def get_branch_if_pushed():
    """
    Get the current branch if it is pushed to the remote repository.

    Returns:
        str or None: The name of the current branch if pushed, None otherwise.
    """
    current_branch = get_current_branch()
    if current_branch not in ["master", "main"] and is_branch_pushed(current_branch):
        return current_branch
    return None


def markdown_panel(title, content, hide_frame=False):
    """
    Create a Rich panel with markdown content that automatically fits the width.

    Args:
        title (str): The title of the panel.
        content (str): The markdown content to display.
        hide_frame (bool, optional): If True, hide the frame of the panel. Defaults to False.

    Returns:
        Panel: The created Rich panel.
    """
    # Calculate width based on the text content
    max_line_length = max(len(line) for line in content.split("\n"))
    padding = 4  # Adjust padding as necessary
    width = max_line_length + padding
    return Panel.fit(
        Markdown(content), title=title, width=width, box=box.MINIMAL if hide_frame else box.ROUNDED
    )


@functools.lru_cache()
def is_git_repo():
    """
    Check if the current directory is part of a Git repository.

    Returns:
        bool: True if the current directory is part of a Git repository, False otherwise.
    """
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
    """
    Get the root directory of the current Git repository.

    Returns:
        str or None: The root directory of the Git repository, or None if not in a Git repository.
    """
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


def get_api_host():
    """
    Get the API host URL.

    Returns:
        str: The API host URL.
    """
    return os.getenv("PR_PILOT_HOST", "https://arcane.engineer")
