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
        display_commands(console, repo, remote_index)
        answers = prompt_user_for_commands(remote_index)
        if not answers:
            return
        local_index = CommandIndex()
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


def display_commands(console, repo, remote_index):
    """Display the commands found in the repository."""
    console.print(f"Found the following commands in {repo}:")
    table = Table(box=None)
    table.add_column("Name", style="cyan bold")
    table.add_column("Description", style="magenta")
    for command in remote_index.get_commands():
        table.add_row(command.name, command.description)
    console.print(Padding(table, (1, 1)))


def prompt_user_for_commands(remote_index):
    """Prompt the user to select commands to import."""
    choices = [cmd.name for cmd in remote_index.get_commands()]
    questions = [
        inquirer.Checkbox(
            "commands",
            message="Which commands would you like to add?",
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
