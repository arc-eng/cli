import click

from cli.command_index import CommandIndex


class RunCommand(click.Group):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.command_index = CommandIndex()

    def list_commands(self, ctx):
        rv = []
        for pilot_command in self.command_index.get_commands():
            rv.append(pilot_command.name)
        rv.sort()
        return rv

    def get_command(self, ctx, name):
        for pilot_command in self.command_index.get_commands():
            if pilot_command.name == name:
                return pilot_command.to_click_command()
        raise click.UsageError(f"Command '{name}' not found.")
