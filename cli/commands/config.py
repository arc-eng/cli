import click
import os
import subprocess
from rich import print
from rich.prompt import Confirm

from cli.constants import CONFIG_LOCATION


@click.group()
def config():
    """🔧 Customize PR Pilots behavior."""
    pass


@config.command()
def edit():
    """Edit the configuration file."""
    config_file = os.path.expanduser(CONFIG_LOCATION)
    click.edit(filename=config_file)


@config.command()
def shell_completion():
    """Add shell completions."""
    shell = os.getenv("SHELL")
    if not shell:
        print(
            "[red]Could not determine the shell. Please set the SHELL environment variable.[/red]"
        )
        return

    shell_name = os.path.basename(shell)

    if shell_name in ["bash", "zsh", "fish"]:
        if shell_name == "bash":
            print("[blue]Add the following line to your ~/.bashrc or ~/.profile:[/blue]")
            print('[cyan]eval "$(_PILOT_COMPLETE=source_bash pilot)"[/cyan]')
            if Confirm.ask(
                "Do you want to add this line to your ~/.bashrc or ~/.profile?", default=True
            ):
                subprocess.run(
                    [
                        "bash",
                        "-c",
                        "echo 'eval \"$(_PILOT_COMPLETE=source_bash pilot)\"' >> ~/.bashrc",
                    ]
                )
        elif shell_name == "zsh":
            print("[blue]Add the following line to your ~/.zshrc:[/blue]")
            print('[cyan]eval "$(_PILOT_COMPLETE=source_zsh pilot)"[/cyan]')
            if Confirm.ask("Do you want to add this line to your ~/.zshrc?", default=True):
                subprocess.run(
                    ["zsh", "-c", "echo 'eval \"$(_PILOT_COMPLETE=source_zsh pilot)\"' >> ~/.zshrc"]
                )
        elif shell_name == "fish":
            print("[blue]Add the following line to your ~/.config/fish/config.fish:[/blue]")
            print("[cyan]eval (env _PILOT_COMPLETE=source_fish pilot)[/cyan]")
            if Confirm.ask(
                "Do you want to add this line to your ~/.config/fish/config.fish?", default=True
            ):
                subprocess.run(
                    [
                        "fish",
                        "-c",
                        "echo 'eval (env _PILOT_COMPLETE=source_fish pilot)' "
                        ">> ~/.config/fish/config.fish",
                    ]
                )
    else:
        print(f"[red]Shell {shell_name} is not supported for automatic completions.[/red]")
