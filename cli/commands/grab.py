import os
import subprocess
import tempfile

import click
import inquirer
from rich.console import Console
from rich.padding import Padding
from rich.prompt import Confirm
from rich.table import Table

from cli.command_index import DEFAULT_FILE_PATH, CommandIndex
from cli.status_indicator import StatusIndicator

from cli.util import PaddedConsole


@click.group()
@click.pass_context
def grab(ctx):
    """🤲 Grab commands, prompts and plans from other repositories."""
    pass


@grab.command("commands")
@click.argument("repo")
@click.pass_context
def grab_commands(ctx, repo):
    """🤲 Grab commands from a Github repository (owner/repo).

    Example: pilot grab commands pr-pilot-ai/pr-pilot-cli
    """
    console = Console()
    status_indicator = StatusIndicator(
        spinner=ctx.obj["spinner"], messages=not ctx.obj["quiet"], console=console
    )
    status_indicator.start()
    # Check out repository to a temporary directory
    full_repo_url = f"git@github.com:{repo}.git"
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Shallow clone repository with subprocess
        status_indicator.update(f"Loading commands from {repo}")
        subprocess.run(
            ["git", "clone", "--depth", "1", full_repo_url, tmp_dir],
            check=True,
            capture_output=True,
        )
        # Load .pilot-commands.yaml from the repository
        full_path = os.path.join(tmp_dir, DEFAULT_FILE_PATH)
        if not os.path.exists(full_path):
            click.ClickException(
                f"Repository {full_repo_url} does not contain a {DEFAULT_FILE_PATH} file."
            )
        status_indicator.stop()
        # Load the commands from the repository
        remote_index = CommandIndex(full_path)
        # Render all commands as a Rich table
        console.print(f"Found the following commands in {repo}:")
        table = Table(box=None)
        table.add_column("Name", style="cyan bold")
        table.add_column("Description", style="magenta")
        for command in remote_index.get_commands():
            table.add_row(command.name, command.description)
        console.print(Padding(table, (1, 1)))
        # Use rich to provide a select list for the user
        choices = [cmd.name for cmd in remote_index.get_commands()]
        questions = [
            inquirer.Checkbox(
                "commands",
                message="Which commands would you like to add?",
                choices=choices,
            ),
        ]
        answers = inquirer.prompt(questions)
        # Add the selected command to the local index
        local_index = CommandIndex()
        files_imported = []
        commands_imported = []
        for command_name in answers["commands"]:
            remote_command = remote_index.get_command(command_name)
            if local_index.get_command(command_name):
                overwrite = Confirm.ask(
                    f"Command {command_name} already exists. Overwrite?"
                )
                if not overwrite:
                    continue
            local_index.remove_command(command_name)
            local_index.add_command(remote_command)
            if remote_command.params.file:
                full_path = os.path.join(tmp_dir, remote_command.params.file)
                # Copy file to local directory
                with open(full_path, "r") as f:
                    content = f.read()
                # Make directories if necessary
                os.makedirs(os.path.dirname(remote_command.params.file), exist_ok=True)
                with open(remote_command.params.file, "w") as f:
                    f.write(content)
                files_imported.append(remote_command.params.file)
            commands_imported.append(remote_command)
        local_index.save_commands()
        console.line()
        if commands_imported:
            console.print(f"You can now use the following commands:")
            table = Table(box=None, show_header=False)
            table.add_column("Command", style="bold")
            table.add_column("Description", style="magenta")
            for command in commands_imported:
                table.add_row(
                    f"[code]pilot run [green]{command.name}[/green][code]",
                    command.description,
                )
            console.print(Padding(table, (1, 1)))
        else:
            console.print("No commands imported.")
