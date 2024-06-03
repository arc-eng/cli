import os
from pathlib import Path

import click
import yaml
from pr_pilot.util import create_task
from rich.console import Console
from rich.markdown import Markdown

from cli.constants import CODE_PRIMER, CHEAP_MODEL, CODE_MODEL, CONFIG_LOCATION, CONFIG_API_KEY
from cli.detect_repository import detect_repository
from cli.prompt_template import PromptTemplate
from cli.status_indicator import StatusIndicator
from cli.task_handler import TaskHandler
from cli.util import load_config


class TaskRunner:
    def __init__(self):
        self.config = load_config()


    def take_screenshot(self):
        screenshot_command = "screencapture -i /tmp/screenshot.png"
        os.system(screenshot_command)
        return Path("/tmp/screenshot.png")

    def run_task(self, wait, repo, snap, edit, spinner, quiet, cheap, code, file, direct, output, model, debug, prompt):
        prompt = ' '.join(prompt)

        console = Console()
        show_spinner = spinner and not quiet
        status = StatusIndicator(spinner=show_spinner, messages=not quiet, console=console)
        screenshot = self.take_screenshot() if snap else None

        if not os.getenv("PR_PILOT_API_KEY"):
            os.environ["PR_PILOT_API_KEY"] = self.config[CONFIG_API_KEY]
        if not repo:
            repo = detect_repository()
        if not repo:
            repo = self.config.get("default_repo")
        if not repo:
            console.print(f"No Github repository provided. Use --repo or set 'default_repo' in {CONFIG_LOCATION}.")
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
            prompt += f"Please edit the file content above in the following way:\n\n{user_prompt}\n\n{CODE_PRIMER}"
            if not output:
                output = edit

        if cheap:
            model = CHEAP_MODEL
        if code:
            prompt += "\n\n" + CODE_PRIMER
            if not model:
                model = CODE_MODEL

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