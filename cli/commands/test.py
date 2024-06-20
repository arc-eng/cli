import click

@click.command()
def test():
    click.echo('test')

if __name__ == '__main__':
    test()