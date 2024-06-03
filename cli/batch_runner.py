import yaml


class BatchRunner:
    def __init__(self, batch_file: str):
        with open(batch_file, 'r') as f:
            self.config = yaml.safe_load(f)
        self.name = self.config.get('name')
        self.tasks = self.config.get('tasks')

    def run(self):
        for task in self.tasks:
            pass