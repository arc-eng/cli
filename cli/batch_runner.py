import yaml

from cli.task_runner import TaskRunner


class BatchRunner:
    def __init__(self, batch_file: str):
        with open(batch_file, 'r') as f:
            self.config = yaml.safe_load(f)
        self.name = self.config.get('name')
        self.tasks = self.config.get('steps')

    def run(self, wait, repo, snap, edit, spinner, quiet, cheap, code, file, direct, output, model, debug, prompt):
        for task in self.tasks:
            # Collect template_file_path, repo, model, output_file, prompt
            template_file_path = task.get('template')
            repo = task.get('repo')
            model = task.get('model')
            output_file = task.get('output_file')
            prompt = task.get('prompt')
            task_runner = TaskRunner()
