import yaml
from rich.console import Console
from rich.markdown import Markdown

from cli.status_indicator import StatusIndicator
from cli.task_runner import TaskRunner
from cli.models import TaskParameters


class PlanExecutor:
    def __init__(self, plan: str, status_indicator: StatusIndicator):
        """Initializes the PlanExecutor class

        :param plan: File path to a plan YAML file
        :param status_indicator: Status indicator
        """
        with open(plan, "r") as f:
            self.plan = yaml.safe_load(f)

        if "name" not in self.plan:
            raise ValueError("Plan must have a name")
        if "steps" not in self.plan:
            raise ValueError("Plan must have steps")
        self.name = self.plan.get("name")
        self.tasks = self.plan.get("steps")
        self.status_indicator = status_indicator
        self.pr_number = None
        self.responses = []

    def run(self, wait, repo, verbose, model, debug):
        """Run all steps in a given plan

        :param wait: Wait for PR Pilot to finish the plan
        :param repo: Github repository in the format owner/repo
        :param verbose: Display more status messages
        :param model: GPT model to use
        :param debug: Display debug information

        """
        console = Console()
        num_tasks = len(self.tasks)
        current_task = 0
        if verbose:
            console.line()
            console.print(f"Running [bold]{self.name}[/bold] with {num_tasks} sub-tasks.")
        for task in self.tasks:
            if verbose:
                console.line()
                console.print(f"( {current_task + 1}/{num_tasks} ) {task.get('name')}")
            current_task += 1
            # Collect template_file_path, repo, model, output_file, prompt
            template_file_path = task.get("template", None)
            repo = task.get("repo", repo)
            model = task.get("model", model)
            output_file = task.get("output_file", None)
            cheap = task.get("cheap", False)
            code = task.get("code", False)
            direct = task.get("direct", False)
            branch = task.get("branch", None)
            snap = False

            previous_responses = ""
            for i, response in enumerate(self.responses):
                previous_responses += f"## Result of Sub-task {i + 1}\n\n{response}\n\n"
            wrapped_prompt = (
                "We are working on a main task that contains a list of sub-tTasks. "
                f"This is sub-task {current_task} / {num_tasks}\n\n---\n\n"
                f"# Main Task {self.name}\n\n{self.plan.get('prompt')}\n\n"
                f"# Results of previous sub-tasks\n\n{previous_responses}\n\n"
                f"# Current Sub-task: {task.get('name')}\n\n{task.get('prompt')}\n\n---\n\n"
                f"Follow the instructions of the current sub-task! "
                f"Respond with a compact bullet list of your actions."
            )
            if debug:
                console.line()
                console.print(Markdown(wrapped_prompt))
                console.line()

            params = TaskParameters(
                wait=wait,
                repo=repo,
                snap=snap,
                verbose=verbose,
                cheap=cheap,
                code=code,
                template_file_path=template_file_path,
                direct=direct,
                output_file=output_file,
                model=model,
                debug=debug,
                prompt=wrapped_prompt,
                branch=branch,
                pr_number=self.pr_number,
            )

            task_runner = TaskRunner(self.status_indicator)
            finished_task = task_runner.run_task(params)
            if not finished_task:
                raise ValueError("Task failed")
            self.responses.append(finished_task.result)
            if self.pr_number is None and finished_task.pr_number and verbose:
                console.print(
                    f"Found new pull request! "
                    f"All subsequent tasks will run on PR #{finished_task.pr_number}"
                )
            self.pr_number = int(finished_task.pr_number) if finished_task.pr_number else None
