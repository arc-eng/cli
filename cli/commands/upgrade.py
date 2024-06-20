import subprocess
import sys

import click
from rich.prompt import Confirm


@click.command()
def upgrade():
    """⬆️ Upgrade pr-pilot-cli to the latest version."""
    if is_installed_via_homebrew():
        if Confirm.ask(
            "Found homebrew installation. Upgrade the [code]pr-pilot-cli[/code] package?"
        ):
            subprocess.run(["brew", "update"], check=True)
            subprocess.run(["brew", "upgrade", "pr-pilot-cli"], check=True)
    else:
        if Confirm.ask("Upgrade the [code]pr-pilot-cli[/code] package with pip?"):
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "--upgrade", "pr-pilot-cli"], check=True
            )


def is_installed_via_homebrew() -> bool:
    """Check if pr-pilot-cli is installed via Homebrew."""
    result = subprocess.run(["brew", "list", "pr-pilot-cli"], capture_output=True)
    return result.returncode == 0
