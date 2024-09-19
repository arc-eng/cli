import webbrowser

import arcane
import click
from arcane import RepoBranchInput
from arcane.exceptions import NotFoundException
from arcane.util import _get_config_from_env

from rich.console import Console

from cli.detect_repository import detect_repository
from cli.status_indicator import StatusIndicator
from cli.util import get_current_branch


@click.command()
@click.option("--no-browser", "-nb", is_flag=True, help="Do not open the PR in a browser.")
@click.pass_context
def pr(ctx, no_browser):
    """🌐 Find and open the pull request for the current branch."""
    # Identify the current Github repo
    if not ctx.obj["repo"]:
        ctx.obj["repo"] = detect_repository()
    repo = ctx.obj["repo"]

    # Identify the current branch
    branch = get_current_branch()
    status_indicator = StatusIndicator(
        spinner=ctx.obj["spinner"], display_log_messages=ctx.obj["verbose"], console=Console()
    )
    status_indicator.update_spinner_message(
        f"Looking for PR number for {repo} on branch {branch}..."
    )
    status_indicator.start()

    # Retrieve the PR number
    with arcane.ApiClient(_get_config_from_env()) as api_client:
        api_instance = arcane.PRRetrievalApi(api_client)
        if not repo:
            raise Exception("Repository not found.")
        try:
            response = api_instance.resolve_pr_create(
                RepoBranchInput(github_repo=repo, branch=branch)
            )
        except NotFoundException:
            status_indicator.stop()
            status_indicator.log_message(
                f"No PR found for branch `{branch}` on repository `{repo}`."
            )
            return
        status_indicator.stop()
        pr_link = f"https://github.com/{repo}/pull/{response.pr_number}"
        status_indicator.log_message(f"Branch `{branch}` has PR [#{response.pr_number}]({pr_link})")
        if not no_browser:
            webbrowser.open(pr_link)
