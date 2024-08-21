import click
from pr_pilot import PRPilot
import subprocess

@click.command()
def pr():
    """Retrieve the PR number for the current branch."""
    try:
        # Identify the current Github repo
        repo_url = subprocess.check_output(['git', 'config', '--get', 'remote.origin.url']).strip().decode('utf-8')
        repo = repo_url.split('.git')[0].split(':')[-1]

        # Identify the current branch
        branch = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).strip().decode('utf-8')

        # Initialize PR Pilot SDK
        pr_pilot = PRPilot()

        # Retrieve the PR number
        pr_number = pr_pilot.get_pr_number(repo, branch)

        click.echo(f"PR Number for {repo} on branch {branch}: {pr_number}")
    except subprocess.CalledProcessError as e:
        click.echo(f"Error retrieving Git information: {e}")
    except Exception as e:
        click.echo(f"Error: {e}")
