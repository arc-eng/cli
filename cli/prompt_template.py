import os
import subprocess
import time

import jinja2
from pr_pilot.util import create_task
from yaspin import yaspin

from cli.task_handler import TaskHandler



def sh(shell_command, spinner=None):
    if spinner:
        spinner.text = f"Running shell command: {shell_command}"
    process = subprocess.Popen(shell_command.split(), stdout=subprocess.PIPE)
    time.sleep(5)
    output, error = process.communicate()
    return output.decode('utf-8')

def read_env_var(variable, default=None):
    """Get the value of an environment variable, with a default value."""
    return os.environ.get(variable, default)


def wrap_function_with_spinner(func, show_spinner=True):
    def wrapper(*args, **kwargs):
        if not show_spinner:
            return func(*args, **kwargs)
        with yaspin() as spinner:
            kwargs['spinner'] = spinner
            return func(*args, **kwargs)

    return wrapper

class PromptTemplate:
    def __init__(self, template_file_path, repo, model):
        self.template_file_path = template_file_path
        self.repo = repo
        self.model = model

    def render(self, show_spinner=True):
        def subtask(prompt, spinner=None):
            try:
                task = create_task(self.repo, prompt, log=False, gpt_model=self.model)
                task_handler = TaskHandler(task, show_spinner)
                return task_handler.wait_for_result(None, False)
            except Exception as e:
                return f"Error: {e}"

        env = jinja2.Environment(loader=jinja2.FileSystemLoader(os.getcwd()))
        env.globals.update(env=read_env_var)
        env.globals.update(subtask=subtask)
        env.globals.update(sh=wrap_function_with_spinner(sh, show_spinner))
        template = env.get_template(self.template_file_path)
        return template.render()
