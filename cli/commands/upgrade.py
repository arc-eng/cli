import subprocess
import sys

import click
from rich.prompt import Confirm


@click.command()
def upgrade():
    """⬆️ Upgrade arcane-engine-cli to the latest version."""
    if is_installed_via_homebrew():
        if Confirm.ask(
            "Found homebrew installation. Upgrade the [code]arcane-engine-cli[/code] package?"
        ):
            subprocess.run(["brew", "update"], check=True)
            subprocess.run(["brew", "upgrade", "arcane-engine-cli"], check=True)
    else:
        if Confirm.ask("Upgrade the [code]arcane-engine-cli[/code] package with pip?"):
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "--upgrade", "arcane-engine-cli"], check=True
            )


def is_installed_via_homebrew() -> bool:
    """Check if arcane-engine-cli is installed via Homebrew."""
    result = subprocess.run(["brew", "list", "arcane-engine-cli"], capture_output=True)
    return result.returncode == 0
