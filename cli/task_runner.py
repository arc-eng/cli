import os
from pathlib import Path

import click
from pr_pilot.util import create_task
from rich.console import Console
from rich.markdown import Markdown

from cli.constants import CODE_PRIMER, CHEAP_MODEL, CODE_MODEL, CONFIG_LOCATION, CONFIG_API_KEY
from cli.detect_repository import detect_repository
from cli.prompt_template import PromptTemplate
from cli.status_indicator import StatusIndicator
from cli.task_handler import TaskHandler
from cli.util import load_config


class TaskConfig:
    def __init__(self, wait, repo, snap, edit, quiet, cheap, code, file, direct, output, model, debug, prompt, branch=None):
        self.wait = wait
        self.repo = repo
        self.snap = snap
        self.edit = edit
        self.quiet = quiet
        self.cheap = cheap
        self.code = code
        self.file = file
        self.direct = direct
        self.output = output
        self.model = model
        self.debug = debug
        self.prompt = prompt
        self.branch = branch


class TaskRunner:
    def __init__(self, status_indicator: StatusIndicator):
        self.config = load_config()
        self.status_indicator = status_indicator

    def take_screenshot(self):
        screenshot_command = "screencapture -i /tmp/screenshot.png"
        os.system(screenshot_command)
        return Path("/tmp/screenshot.png")

    def run_task(self, config: TaskConfig):
        prompt = ' '.join(config.prompt)

        console = Console()
        screenshot = self.take_screenshot() if config.snap else None

        if not os.getenv("PR_PILOT_API_KEY"):
            os.environ["PR_PILOT_API_KEY"] = self.config[CONFIG_API_KEY]
        if not config.repo:
            config.repo = detect_repository()
        if not config.repo:
            config.repo = self.config.get("default_repo")
        if not config.repo:
            console.print(f"No Github repository provided. Use --repo or set 'default_repo' in {CONFIG_LOCATION}.")
            return
        if config.file:
            self.status_indicator.start()
            renderer = PromptTemplate(config.file, config.repo, config.model, self.status_indicator)
            prompt = renderer.render()
        if not prompt:
            prompt = click.edit("", extension=".md")
            if not prompt:
                console.print("No prompt provided.")
                return

        if config.edit:
            file_content = Path(config.edit).read_text()
            user_prompt = prompt
            prompt = f"I have the following file content:\n\n---\n{file_content}\n---\n\n"
            prompt += f"Please edit the file content above in the following way:\n\n{user_prompt}\n\n{CODE_PRIMER}"
            if not config.output:
                config.output = config.edit

        if config.cheap:
            config.model = CHEAP_MODEL
        if config.code:
            prompt += "\n\n" + CODE_PRIMER
            if not config.model:
                config.model = CODE_MODEL

        if config.direct:
            if config.output:
                with open(config.output, "w") as f:
                    f.write(prompt)
                self.status_indicator.stop()
                if not config.quiet:
                    console.line()
                    console.print(Markdown(f"Rendered template `{config.file}` into `{config.output}`"))
                    console.line()
                return
        self.status_indicator.start()

        branch_str = f"on branch {config.branch}" if config.branch else ""
        self.status_indicator.update(f"Creating new task for {config.repo} {branch_str} ...")
        task = create_task(config.repo, prompt, log=False, gpt_model=config.model, image=screenshot, branch=config.branch)
        self.status_indicator.update(f"Task created: https://app.pr-pilot.ai/dashboard/tasks/{task.id}")
        self.status_indicator.success()
        if config.debug:
            console.print(task)
        if config.wait:
            task_handler = TaskHandler(task, self.status_indicator)
            task_handler.wait_for_result(config.output, config.quiet)
        self.status_indicator.stop()
        if config.debug:
            console.print(task)