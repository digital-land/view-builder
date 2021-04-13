import click


@click.group()
def cli():
    pass


@click.command()
@click.argument("input_path", type=click.Path(exists=True))
@click.argument("output_path", type=click.Path(exists=False))
def build(input_path, output_path):
    pass


cli.add_command(build)
