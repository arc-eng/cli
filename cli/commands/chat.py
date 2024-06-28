import click
from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Confirm

from cli.models import TaskParameters
from cli.status_indicator import StatusIndicator
from cli.task_runner import TaskRunner


@click.command()
def chat():
    """💬 Chat with PR Pilot."""
    console = Console()
    status_indicator = StatusIndicator(messages=False, spinner=True, console=console)
    task_runner = TaskRunner(status_indicator)
    chat_history = []

    while True:
        user_input = console.input("[bold green]You:[/bold green] ")
        if user_input.strip() == "":
            break
        chat_history.append({"role": "user", "content": user_input})
        params = TaskParameters(prompt=user_input, wait=True)
        task = task_runner.run_task(params, print_result=False, print_task_id=False)
        if task:
            chat_history.append({"role": "assistant", "content": task.result})
            console.print("[bold blue]AI:[/bold blue]")
            console.print(Markdown(task.result))

    if Confirm.ask("Do you want to save the chat history to a file?", default="n"):
        file_path = console.input("Enter the file path to save the chat history: ")
        with open(file_path, "w") as f:
            for entry in chat_history:
                f.write(f"{entry['role']}: {entry['content']}\n---\n")
        console.print(f"Chat history saved to {file_path}")
