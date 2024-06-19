import click
import os

@click.group()
def config():
    """Configuration related commands."""
    pass

@config.command()
def shell_completions():
    """Add shell completions for the PR Pilot CLI."""
    shell = os.getenv('SHELL')
    if not shell:
        click.echo('Could not determine the shell. Please set the SHELL environment variable.')
        return

    shell_name = os.path.basename(shell)

    if shell_name in ['bash', 'zsh', 'fish']:
        click.echo(f'Adding completions for {shell_name} shell...')
        click.echo('Follow the instructions below to enable completions:')
        if shell_name == 'bash':
            click.echo('Add the following line to your ~/.bashrc or ~/.profile:')
            click.echo('eval "$(_PR_PILOT_COMPLETE=source_bash pr-pilot)"')
        elif shell_name == 'zsh':
            click.echo('Add the following line to your ~/.zshrc:')
            click.echo('eval "$(_PR_PILOT_COMPLETE=source_zsh pr-pilot)"')
        elif shell_name == 'fish':
            click.echo('Add the following line to your ~/.config/fish/config.fish:')
            click.echo('eval (env _PR_PILOT_COMPLETE=source_fish pr-pilot)')
    else:
        click.echo(f'Shell {shell_name} is not supported for automatic completions.')
