import subprocess
import sys

import click
from rich.prompt import Confirm


@click.command()
def upgrade():
    """⬆️ Upgrade arcane-cli to the latest version."""
    if is_installed_via_homebrew():
        if Confirm.ask(
            "Found homebrew installation. Upgrade the [code]arcane-cli[/code] package?"
        ):
            subprocess.run(["brew", "update"], check=True)
            subprocess.run(["brew", "upgrade", "arcane-cli"], check=True)
    else:
        if Confirm.ask("Upgrade the [code]arcane-cli[/code] package with pip?"):
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "--upgrade", "arcane-cli"], check=True
            )


def is_installed_via_homebrew() -> bool:
    """Check if arcane-cli is installed via Homebrew."""
    result = subprocess.run(["brew", "list", "arcane-cli"], capture_output=True)
    return result.returncode == 0
