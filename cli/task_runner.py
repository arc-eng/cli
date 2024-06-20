import os
from pathlib import Path
from typing import Optional

import click
from pr_pilot import Task
from pr_pilot.util import create_task
from rich.console import Console
from rich.markdown import Markdown
from rich.padding import Padding

from cli.constants import CODE_PRIMER, CHEAP_MODEL, CODE_MODEL, CONFIG_LOCATION
from cli.detect_repository import detect_repository
from cli.models import TaskParameters
from cli.prompt_template import PromptTemplate
from cli.status_indicator import StatusIndicator
from cli.task_handler import TaskHandler
from cli.util import load_config


class TaskRunner:
    def __init__(self, status_indicator: StatusIndicator):
        self.config = load_config()
        self.status_indicator = status_indicator

    def take_screenshot(self):
        screenshot_command = "screencapture -i /tmp/screenshot.png"
        os.system(screenshot_command)
        return Path("/tmp/screenshot.png")

    def run_task(self, params: TaskParameters) -> Optional[Task]:

        console = Console()
        screenshot = self.take_screenshot() if params.snap else None

        if not params.repo:
            params.repo = detect_repository()
        if not params.repo:
            params.repo = self.config.get("default_repo")
        if not params.repo:
            console.print(
                f"No Github repository provided. "
                f"Use --repo or set 'default_repo' in {CONFIG_LOCATION}."
            )
            return None
        if params.file:
            renderer = PromptTemplate(params.file, params.repo, params.model, self.status_indicator)
            params.prompt = renderer.render()
        if not params.prompt:
            params.prompt = click.edit("", extension=".md")
            if not params.prompt:
                console.print("No prompt provided.")
                return None

        if params.pr_number:
            params.prompt = (
                f"We are working on PR #{params.pr_number}. "
                "Read the PR first before doing anything else.\n\n---\n\n" + params.prompt
            )

        if params.cheap:
            params.model = CHEAP_MODEL
        if params.code:
            params.prompt += "\n\n" + CODE_PRIMER
            if not params.model:
                params.model = CODE_MODEL

        if params.direct:
            if params.output:
                with open(params.output, "w") as f:
                    f.write(params.prompt)
                self.status_indicator.stop()
                if not params.verbose:
                    console.line()
                    console.print(
                        Markdown(f"Rendered template `{params.file}` into `{params.output}`")
                    )
                    console.line()
                return

        branch_str = f" on branch [code]{params.branch}[/code]" if params.branch else ""
        pr_link = (
            (
                f"[link=https://github.com/{params.repo}/pull/{params.pr_number}]"
                f"PR #{params.pr_number}[/link]"
            )
            if params.pr_number
            else ""
        )
        task = create_task(
            params.repo,
            params.prompt,
            log=False,
            gpt_model=params.model,
            image=screenshot,
            branch=params.branch,
            pr_number=params.pr_number,
        )

        if not params.verbose:
            # Status messages are only visible in verbose mode, so let's print the new task ID
            message = (
                f"✔ [bold][green]Task created[/green]: "
                f"[link=https://app.pr-pilot.ai/dashboard/tasks/{task.id}/]{task.id}[/link][/bold]"
                f"{branch_str}{pr_link}"
            )
            console.print(Padding(message, (0, 0)))
            self.status_indicator.start()
        else:
            self.status_indicator.start()
            self.status_indicator.update(f"Task created: {task.id}")
            self.status_indicator.success(start_again=True)

        if params.debug:
            console.print(task)
        task_handler = None
        if params.wait:
            task_handler = TaskHandler(task, self.status_indicator)
            task_handler.wait_for_result(params.output, params.verbose, code=params.code)
        self.status_indicator.stop()
        if params.debug:
            console.print(task)
        return task_handler.task if task_handler else task
