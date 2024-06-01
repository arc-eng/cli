import os
import subprocess

import click
import jinja2
from pr_pilot.util import create_task

from cli.task_handler import TaskHandler


def sh(shell_command, status):
    status.update(f"Running shell command: {shell_command}")
    try:
        process = subprocess.Popen(shell_command.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()
        status.success()
        return output.decode('utf-8')
    except Exception as e:
        click.echo(str(e))
        status.fail()


def read_env_var(variable, default=None):
    """Get the value of an environment variable, with a default value."""
    return os.environ.get(variable, default)


def wrap_function_with_status(func, status):
    def wrapper(*args, **kwargs):
        kwargs['status'] = status
        return func(*args, **kwargs)

    return wrapper


class PromptTemplate:
    def __init__(self, template_file_path, repo, model, status):
        self.template_file_path = template_file_path
        self.repo = repo
        self.model = model
        self.status = status

    def render(self):

        def subtask(prompt, status):
            # Treat prompt as a file path and read the content if the file exists
            # The file name will be relative to the current jinja template
            full_template_path = os.path.join(os.getcwd(), self.template_file_path)
            current_template_path = os.path.dirname(full_template_path)
            potential_file_path = os.path.join(current_template_path, prompt)
            if os.path.exists(potential_file_path):
                with open(potential_file_path, 'r') as f:
                    status.update(f"Loaded prompt from file: {prompt}")
                    status.success()
                    prompt = f.read()

            try:
                status.update("Creating sub-task ...")
                task = create_task(self.repo, prompt, log=False, gpt_model=self.model)
                task_handler = TaskHandler(task, status)
                return task_handler.wait_for_result(quiet=True)
            except Exception as e:
                return f"Error: {e}"

        env = jinja2.Environment(loader=jinja2.FileSystemLoader(os.getcwd()))
        env.globals.update(env=read_env_var)
        env.globals.update(subtask=wrap_function_with_status(subtask, self.status))
        env.globals.update(sh=wrap_function_with_status(sh, self.status))
        template = env.get_template(self.template_file_path)
        return template.render()
