import click

from deps_file_storage.app import run_api, run_consumer


@click.group()
def cli() -> None:
    pass


@cli.command()
def serve() -> None:
    run_api()


@cli.command()
def listen() -> None:
    pass


@cli.command()
def consume() -> None:
    run_consumer()


if __name__ == "__main__":
    cli()
