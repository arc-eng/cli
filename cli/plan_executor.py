import yaml
from rich.console import Console

from cli.status_indicator import StatusIndicator
from cli.task_runner import TaskRunner


class PlanExecutor:
    def __init__(self, plan: str, status_indicator: StatusIndicator):
        """Initializes the PlanExecutor class

        :param plan: File path to a plan YAML file
        :param status_indicator: Status indicator
        """
        with open(plan, 'r') as f:
            self.plan = yaml.safe_load(f)

        if 'name' not in self.plan:
            raise ValueError('Plan must have a name')
        if 'steps' not in self.plan:
            raise ValueError('Plan must have steps')
        self.name = self.plan.get('name')
        self.tasks = self.plan.get('steps')
        self.status_indicator = status_indicator

    def run(self, wait, repo, edit, quiet, model, debug, prompt):
        """Run all steps in a given plan

        :param wait: Wait for PR Pilot to finish the plan
        :param repo: Github repository in the format owner/repo
        :param edit: Let PR Pilot edit a file for you
        :param quiet: Disable all output on the terminal
        :param model: GPT model to use
        :param debug: Display debug information
        :param prompt: Prompt for the task

        """
        console = Console()
        num_tasks = len(self.tasks)
        current_task = 0
        if not quiet:
            console.line()
            console.print(f"Running [bold]{self.name}[/bold] with {num_tasks} sub-tasks.")
        for task in self.tasks:
            if not quiet:
                console.line()
                console.print(f"( {current_task + 1}/{num_tasks} ) {task.get('name')}")
            current_task += 1
            # Collect template_file_path, repo, model, output_file, prompt
            template_file_path = task.get('template', None)
            repo = task.get('repo', repo)
            model = task.get('model', model)
            output_file = task.get('output_file', None)
            cheap = task.get('cheap', False)
            code = task.get('code', False)
            direct = task.get('direct', False)
            snap = False

            wrapped_prompt = (f"We are working on a main task that contains a list of sub-tasks. This is sub-task {current_task} / {num_tasks}\n\n---\n\n"
                              f"Main Task: {self.name}\n\n{prompt}\n\n---\n\n"
                              f"Sub-task: {task.get('name')}\n\n{task.get('prompt')}\n\n---\n\n"
                              f"Execute the sub-task")

            prompt = task.get('prompt')
            task_runner = TaskRunner(self.status_indicator)
            task_runner.run_task(wait, repo, snap, edit, quiet, cheap, code, template_file_path, direct, output_file, model, debug, wrapped_prompt)
