import os
from pathlib import Path

import click
import yaml
from pr_pilot.util import create_task
from rich.console import Console
from rich.markdown import Markdown

from cli.detect_repository import detect_repository
from cli.prompt_template import PromptTemplate
from cli.status_indicator import StatusIndicator
from cli.task_handler import TaskHandler


class TaskRunner:
    def __init__(self, config_location, config_api_key, code_model, cheap_model, code_primer, default_model):
        self.config_location = config_location
        self.config_api_key = config_api_key
        self.code_model = code_model
        self.cheap_model = cheap_model
        self.code_primer = code_primer
        self.default_model = default_model

    def load_config(self):
        if not os.path.exists(self.config_location):
            if os.getenv("PR_PILOT_API_KEY"):
                click.echo("Using API key from environment variable.")
                api_key = os.getenv("PR_PILOT_API_KEY")
            else:
                api_key_url = "https://app.pr-pilot.ai/dashboard/api-keys/"
                click.echo(f"Configuration file not found. Please create an API key at {api_key_url}.")
                api_key = click.prompt("PR Pilot API key")
            with open(self.config_location, "w") as f:
                f.write(f"{self.config_api_key}: {api_key}")
            click.echo(f"Configuration saved in {self.config_location}")
        with open(self.config_location) as f:
            config = yaml.safe_load(f)
        return config

    def take_screenshot(self):
        screenshot_command = "screencapture -i /tmp/screenshot.png"
        os.system(screenshot_command)
        return Path("/tmp/screenshot.png")

    def run_task(self, wait, repo, snap, edit, spinner, quiet, cheap, code, file, direct, output, model, debug, prompt):
        prompt = ' '.join(prompt)
        config = self.load_config()
        console = Console()
        show_spinner = spinner and not quiet
        status = StatusIndicator(spinner=show_spinner, messages=not quiet, console=console)
        screenshot = self.take_screenshot() if snap else None

        if not os.getenv("PR_PILOT_API_KEY"):
            os.environ["PR_PILOT_API_KEY"] = config[self.config_api_key]
        if not repo:
            repo = detect_repository()
        if not repo:
            repo = config.get("default_repo")
        if not repo:
            console.print(f"No Github repository provided. Use --repo or set 'default_repo' in {self.config_location}.")
            return
        if file:
            status.start()
            renderer = PromptTemplate(file, repo, model, status)
            prompt = renderer.render()
        if not prompt:
            prompt = click.edit("", extension=".md")
            if not prompt:
                console.print("No prompt provided.")
                return

        if edit:
            file_content = Path(edit).read_text()
            user_prompt = prompt
            prompt = f"I have the following file content:\n\n---\n{file_content}\n---\n\n"
            prompt += f"Please edit the file content above in the following way:\n\n{user_prompt}\n\n{self.code_primer}"
            if not output:
                output = edit

        if cheap:
            model = self.cheap_model
        if code:
            prompt += "\n\n" + self.code_primer
            if not model:
                model = self.code_model

        if direct:
            if output:
                with open(output, "w") as f:
                    f.write(prompt)
                status.stop()
                if not quiet:
                    console.line()
                    console.print(Markdown(f"Rendered template `{file}` into `{output}`"))
                    console.line()
                return
        status.start()
        status.update("Creating new task")
        task = create_task(repo, prompt, log=False, gpt_model=model, image=screenshot)
        status.update(f"Task created: https://app.pr-pilot.ai/dashboard/tasks/{task.id}")
        status.success()
        if debug:
            console.print(task)
        if wait:
            task_handler = TaskHandler(task, status)
            task_handler.wait_for_result(output, quiet)
        status.stop()
        if debug:
            console.print(task)