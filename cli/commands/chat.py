import json
import os
from typing import List, Optional

import click
from pydantic import BaseModel, Field
from rich import print
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm

from cli.detect_repository import detect_repository
from cli.models import TaskParameters
from cli.status_indicator import StatusIndicator
from cli.task_runner import TaskRunner
from cli.util import get_branch_if_pushed, markdown_panel


class ChatMessage(BaseModel):
    role: str
    content: str

    def print(self):
        """Print the chat message"""
        if self.role == "user":
            print(Panel(f"[blue]{self.content}[/blue]", expand=False, title="You"))
        elif self.role == "assistant":
            print(markdown_panel(None, self.content, hide_frame=True))


class ChatHistory(BaseModel):
    messages: List[ChatMessage] = Field(default=[])
    file: Optional[str] = Field(default=None)

    def print(self):
        """Print the chat history"""
        for msg in self.messages:
            msg.print()

    def dump(self):
        """Dump chat history to JSON file"""
        json.dump([msg.dict() for msg in self.messages], open(self.file, "w"))

    def append(self, message: ChatMessage):
        """Append a message to the chat history"""
        self.messages.append(message)

    def load(self):
        """Load chat history from JSON file. Create it if it doesn't exist."""
        if not self.file:
            raise ValueError("No file path provided.")
        if not os.path.exists(self.file):
            with open(self.file, "w") as f:
                json.dump([], f)
                return
        self.messages = [ChatMessage(**msg) for msg in json.load(open(self.file, "r"))]

    def to_prompt(self):
        """Convert chat history to a prompt"""
        history = "\n\n---\n\n".join(
            [f"{msg.role.upper()}: {msg.content}" for msg in self.messages]
        )
        prompt = "We're having a conversation. Here's the chat history:\n\n" + history
        return prompt + "\n\n---\nRespond to the last message above."


@click.command()
@click.option(
    "--branch",
    "-b",
    help="Chat in the context of a specific branch.",
    required=False,
    default=None,
)
@click.option(
    "--history",
    "-h",
    type=click.Path(exists=True),
    help="Chat history file to load.",
    required=False,
    default=None,
)
@click.pass_context
def chat(ctx, branch, history):
    """💬 Chat with PR Pilot."""
    console = Console()
    status_indicator = StatusIndicator(
        display_log_messages=True, spinner=True, console=console, display_spinner_text=False
    )
    task_runner = TaskRunner(status_indicator)
    chat_history = ChatHistory(file=history, messages=[])

    if chat_history.file:
        # There is an existing conversation. Load and print it.
        welcome_message = (
            f"Continuing conversation from [code][yellow]{chat_history.file}[/yellow][/code]"
        )
        chat_history.load()
        chat_history.print()
    else:
        welcome_message = "Starting a new conversation"

    if not ctx.obj["repo"]:
        ctx.obj["repo"] = detect_repository()

    welcome_message += f" on [code][bold]{ctx.obj['repo']}[/bold][/code]"
    if ctx.obj["sync"]:
        ctx.obj["branch"] = get_branch_if_pushed()
        if not branch and ctx.obj["branch"]:
            branch = ctx.obj["branch"]

    if branch:
        welcome_message += f" in branch [code]{branch}[/code]"
    print("[dim]" + welcome_message + "[/dim]\n")

    run_chat(branch, chat_history, console, ctx, task_runner)

    # If we have a file, automatically save the chat history
    if chat_history.file:
        chat_history.dump()
        print(f"Chat history saved to [code][yellow]{chat_history.file}[/yellow][/code]")
    # Otherwise, ask the user if they want to save the chat history
    elif Confirm.ask("Do you want to save the chat history as a JSON file?", default=False):
        file_path = console.input("Enter the file path to save the chat history: ")
        chat_history.file = file_path
        chat_history.dump()
        print(f"Chat history saved to [code]{file_path}[/code]")


def run_chat(branch, chat_history, console, ctx, task_runner):
    while True:
        user_input = console.input("[bold blue]You:[/bold blue] ")
        if user_input.strip() == "":
            break
        chat_history.append(ChatMessage(role="user", content=user_input))
        params = TaskParameters(
            verbose=True,
            prompt=chat_history.to_prompt(),
            wait=True,
            sync=False,
            branch=branch,
            repo=ctx.obj["repo"],
            model=ctx.obj["model"],
        )
        task = task_runner.run_task(params, print_result=False, print_task_id=False)
        if task:
            response = ChatMessage(role="assistant", content=task.result)
            chat_history.append(response)
            response.print()
