import os
import subprocess
import tempfile

import click
import inquirer
from rich.console import Console
from rich.padding import Padding
from rich.prompt import Confirm
from rich.table import Table
from rich.text import Text

from cli.command_index import DEFAULT_FILE_PATH, CommandIndex
from cli.status_indicator import StatusIndicator


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
        spinner=ctx.obj["spinner"], messages=ctx.obj["verbose"], console=console
    )
    status_indicator.start()
    full_repo_url = f"git@github.com:{repo}.git"
    with tempfile.TemporaryDirectory() as tmp_dir:
        clone_repository(status_indicator, full_repo_url, tmp_dir)
        full_path = os.path.join(tmp_dir, DEFAULT_FILE_PATH)
        if not os.path.exists(full_path):
            click.ClickException(
                f"Repository {full_repo_url} does not contain a {DEFAULT_FILE_PATH} file."
            )
        status_indicator.stop()
        remote_index = CommandIndex(full_path)
        local_index = CommandIndex()
        display_commands(console, repo, local_index, remote_index)
        answers = prompt_user_for_commands(local_index, remote_index)
        if not answers:
            return

        commands_imported, files_imported = import_commands(
            answers, remote_index, local_index, tmp_dir
        )
        local_index.save_commands()
        display_imported_commands(console, commands_imported)


def clone_repository(status_indicator, full_repo_url, tmp_dir):
    """Clone the repository to a temporary directory."""
    status_indicator.update(f"Loading commands from {full_repo_url}")
    subprocess.run(
        ["git", "clone", "--depth", "1", full_repo_url, tmp_dir],
        check=True,
        capture_output=True,
    )


def display_commands(console, repo, local_index, remote_index):
    """Display the commands found in the repository."""
    table = Table(box=None, show_header=True)
    table.add_column(repo)
    table.add_column("")
    local_command_names = [cmd.name for cmd in local_index.get_commands()]
    for command in remote_index.get_commands():
        if command.name in local_command_names:
            # give name grey color if already exists in local index
            table.add_row(
                Text(command.name, style="bright_black"),
                Text(command.description, style="bright_black"),
            )
        else:
            table.add_row(
                Text(command.name, style="bold blue"), Text(command.description, style="bold")
            )
    console.print(Padding(table, (1, 6)))


def prompt_user_for_commands(local_index, remote_index):
    """Prompt the user to select commands to import."""
    local_command_names = [cmd.name for cmd in local_index.get_commands()]
    choices = [
        cmd.name for cmd in remote_index.get_commands() if cmd.name not in local_command_names
    ]
    questions = [
        inquirer.Checkbox(
            "commands",
            message="Grab",
            choices=choices,
        ),
    ]
    return inquirer.prompt(questions)


def import_commands(answers, remote_index, local_index, tmp_dir):
    """Import the selected commands into the local index."""
    files_imported = []
    commands_imported = []
    for command_name in answers["commands"]:
        remote_command = remote_index.get_command(command_name)
        if local_index.get_command(command_name):
            overwrite = Confirm.ask(f"Command {command_name} already exists. Overwrite?")
            if not overwrite:
                continue
        local_index.remove_command(command_name)
        local_index.add_command(remote_command)
        if remote_command.params.file:
            full_path = os.path.join(tmp_dir, remote_command.params.file)
            copy_file_to_local_directory(full_path, remote_command.params.file)
            files_imported.append(remote_command.params.file)
        commands_imported.append(remote_command)
    return commands_imported, files_imported


def copy_file_to_local_directory(source_path, destination_path):
    """Copy a file from the source path to the local directory."""
    with open(source_path, "r") as f:
        content = f.read()
    os.makedirs(os.path.dirname(destination_path), exist_ok=True)
    with open(destination_path, "w") as f:
        f.write(content)


def display_imported_commands(console, commands_imported):
    """Display the imported commands."""
    console.line()
    if commands_imported:
        console.print("You can now use the following commands:")
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
