import os
from pathlib import Path
from typing import Optional

import click
from pr_pilot import Task
from pr_pilot.util import create_task
from rich.console import Console
from rich.markdown import Markdown

from cli.constants import CODE_PRIMER, CHEAP_MODEL, CODE_MODEL, CONFIG_LOCATION, CONFIG_API_KEY
from cli.detect_repository import detect_repository
from cli.prompt_template import PromptTemplate
from cli.status_indicator import StatusIndicator
from cli.task_handler import TaskHandler
from cli.util import load_config
from cli.models import TaskParameters


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

        if not os.getenv("PR_PILOT_API_KEY"):
            os.environ["PR_PILOT_API_KEY"] = self.config[CONFIG_API_KEY]
        if not params.repo:
            params.repo = detect_repository()
        if not params.repo:
            params.repo = self.config.get("default_repo")
        if not params.repo:
            console.print(f"No Github repository provided. Use --repo or set 'default_repo' in {CONFIG_LOCATION}.")
            return None
        if params.file:
            self.status_indicator.start()
            renderer = PromptTemplate(params.file, params.repo, params.model, self.status_indicator)
            params.prompt = renderer.render()
        if not params.prompt:
            params.prompt = click.edit("", extension=".md")
            if not params.prompt:
                console.print("No prompt provided.")
                return None

        if params.pr_number:
            params.prompt = f"We are working on PR #{params.pr_number}. Read the PR first before doing anything else.\n\n---\n\n" + params.prompt

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
                if not params.quiet:
                    console.line()
                    console.print(Markdown(f"Rendered template `{params.file}` into `{params.output}`"))
                    console.line()
                return
        self.status_indicator.start()

        branch_str = f"on branch {params.branch}" if params.branch else ""
        pr_str = f" for PR #{params.pr_number}" if params.pr_number else ""
        self.status_indicator.update(f"Creating new task for {params.repo} {branch_str} ...")
        task = create_task(params.repo, params.prompt, log=False, gpt_model=params.model, image=screenshot, branch=params.branch, pr_number=params.pr_number)
        self.status_indicator.update(f"Task created{pr_str}: https://app.pr-pilot.ai/dashboard/tasks/{task.id}")
        self.status_indicator.success()
        if params.debug:
            console.print(task)
        task_handler = None
        if params.wait:
            task_handler = TaskHandler(task, self.status_indicator)
            task_handler.wait_for_result(params.output, params.quiet, code=params.code)
        self.status_indicator.stop()
        if params.debug:
            console.print(task)
        return task_handler.task if task_handler else task
