import os

import click

from cli.commands.edit import edit
from cli.commands.history import history
from cli.commands.plan import plan
from cli.commands.run import RunCommand
from cli.commands.task import task
from cli.constants import DEFAULT_MODEL, CONFIG_API_KEY
from cli.util import load_config


@click.group()
@click.option('--wait/--no-wait', is_flag=True, default=True, help='Wait for PR Pilot to finish the task.')
@click.option('--repo', help='Github repository in the format owner/repo.', required=False)
@click.option('--spinner/--no-spinner', is_flag=True, default=True, help='Display a loading indicator.')
@click.option('--quiet/--chatty', is_flag=True, default=False, help='Disable all status messages.')
@click.option('--model', '-m', help='GPT model to use.', default=DEFAULT_MODEL)
@click.option('--branch', '-b', help='Run the task on a specific branch.', required=False, default=None)
@click.option('--sync/--no-sync', is_flag=True, default=False, help='Run task on your current branch and pull PR Pilots changes when done.')
@click.option('--debug', is_flag=True, default=False, help='Display debug information.')
@click.pass_context
def main(ctx, wait, repo, spinner, quiet, model, branch, sync, debug):
    """PR Pilot CLI - https://docs.pr-pilot.ai

    Delegate routine work to AI with confidence and predictability.

    Examples:

    \b
    - 📸 Create a Bootstrap5 component based on a screenshot:
      pilot task -o component.html --code --snap "Write a Bootstrap5 component that looks like this."

    \b
    - 🛠️ Refactor and clean up code:
      pilot edit main.js "Break up large functions, organize the file and add comments."

    \b
    - 🔄 Interact across services and tools:
      pilot task "Find all open Linear and Github issues labeled as 'bug' and send them to the #bugs Slack channel."
    """

    user_config = load_config()

    if not os.getenv("PR_PILOT_API_KEY"):
        os.environ["PR_PILOT_API_KEY"] = user_config[CONFIG_API_KEY]

    # If repo is set manually, don't auto sync
    if repo:
        sync = False
    else:
        sync = user_config.get('auto_sync', sync)

    ctx.ensure_object(dict)
    ctx.obj['wait'] = wait
    ctx.obj['repo'] = repo
    ctx.obj['spinner'] = spinner
    ctx.obj['quiet'] = user_config.get('quiet', quiet)
    ctx.obj['model'] = model
    ctx.obj['branch'] = branch
    ctx.obj['sync'] = sync
    ctx.obj['debug'] = debug


main.add_command(task)
main.add_command(edit)
main.add_command(plan)
main.add_command(history)

main.add_command(RunCommand(name="run", help="🚀 Run a saved command."))


if __name__ == '__main__':
    main()
