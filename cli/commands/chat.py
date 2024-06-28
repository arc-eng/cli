import click
from rich.console import Console
from cli.task_runner import TaskRunner
from cli.task_handler import TaskHandler
from cli.status_indicator import StatusIndicator
from cli.models import TaskParameters

@click.command()
def chat():
    console = Console()
    status_indicator = StatusIndicator()
    task_runner = TaskRunner(status_indicator)
    chat_history = []

    while True:
        user_input = console.input("[bold green]You:[/bold green] ")
        if user_input.strip() == "":
            break
        chat_history.append({"role": "user", "content": user_input})
        params = TaskParameters(prompt=user_input, wait=True)
        task = task_runner.run_task(params)
        if task:
            chat_history.append({"role": "assistant", "content": task.result})
            console.print(f"[bold blue]AI:[/bold blue] {task.result}")

    save_history = console.input("Do you want to save the chat history to a file? (y/n): ")
    if save_history.lower() == "y":
        file_path = console.input("Enter the file path to save the chat history: ")
        with open(file_path, "w") as f:
            for entry in chat_history:
                f.write(f"{entry['role']}: {entry['content']}\n")
        console.print(f"Chat history saved to {file_path}")
