import os
import subprocess

import jinja2
from pr_pilot.util import create_task

from cli.task_handler import TaskHandler


def sh(shell_command):
    process = subprocess.Popen(shell_command.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    return output.decode('utf-8')

def render_prompt_template(template_file_path, repo, model):

    def subtask(prompt):
        try:
            task = create_task(repo, prompt, log=False, gpt_model=model)
            task_handler = TaskHandler(task)
            return task_handler.wait_for_result(None, False)
        except Exception as e:
            return f"Error: {e}"

    env = jinja2.Environment(loader=jinja2.FileSystemLoader(os.getcwd()))
    env.globals.update(subtask=subtask)
    env.globals.update(sh=sh)
    template = env.get_template(template_file_path)
    return template.render()
