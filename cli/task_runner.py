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


class TaskRunner:
    def __init__(self, status_indicator: StatusIndicator):
        self.config = load_config()
        self.status_indicator = status_indicator

    def take_screenshot(self):
        screenshot_command = "screencapture -i /tmp/screenshot.png"
        os.system(screenshot_command)
        return Path("/tmp/screenshot.png")

    def run_task(self, wait, repo, snap, quiet, cheap, code, file, direct, output, model, debug, prompt, branch=None, pr_number=None) -> Optional[Task]:

        console = Console()
        screenshot = self.take_screenshot() if snap else None

        if not os.getenv("PR_PILOT_API_KEY"):
            os.environ["PR_PILOT_API_KEY"] = self.config[CONFIG_API_KEY]
        if not repo:
            repo = detect_repository()
        if not repo:
            repo = self.config.get("default_repo")
        if not repo:
            console.print(f"No Github repository provided. Use --repo or set 'default_repo' in {CONFIG_LOCATION}.")
            return None
        if file:
            self.status_indicator.start()
            renderer = PromptTemplate(file, repo, model, self.status_indicator)
            prompt = renderer.render()
        if not prompt:
            prompt = click.edit("", extension=".md")
            if not prompt:
                console.print("No prompt provided.")
                return None

        if pr_number:
            prompt = f"We are working on PR #{pr_number}. Read the PR first before doing anything else.\n\n---\n\n" + prompt


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
                self.status_indicator.stop()
                if not quiet:
                    console.line()
                    console.print(Markdown(f"Rendered template `{file}` into `{output}`"))
                    console.line()
                return
        self.status_indicator.start()

        branch_str = f"on branch {branch}" if branch else ""
        pr_str = f" for PR #{pr_number}" if pr_number else ""
        self.status_indicator.update(f"Creating new task for {repo} {branch_str} ...")
        task = create_task(repo, prompt, log=False, gpt_model=model, image=screenshot, branch=branch, pr_number=pr_number)
        self.status_indicator.update(f"Task created{pr_str}: https://app.pr-pilot.ai/dashboard/tasks/{task.id}")
        self.status_indicator.success()
        if debug:
            console.print(task)
        task_handler = None
        if wait:
            task_handler = TaskHandler(task, self.status_indicator)
            task_handler.wait_for_result(output, quiet, code=code)
        self.status_indicator.stop()
        if debug:
            console.print(task)
        return task_handler.task if task_handler else task
