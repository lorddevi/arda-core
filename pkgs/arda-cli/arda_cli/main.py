"""Arda CLI main entry point"""

import click


@click.group()
@click.version_option(version="0.1.0")
def main() -> None:
    """Arda - minimal infrastructure management for NixOS"""
    pass


@main.command()
def host() -> None:
    """Host management commands"""
    click.echo("Host management - coming soon")


@main.command()
def roles() -> None:
    """Role management commands"""
    click.echo("Role management - coming soon")


@main.command()
def secrets() -> None:
    """Secret management commands"""
    click.echo("Secret management - coming soon")


@main.command()
def templates() -> None:
    """Template management commands"""
    click.echo("Template management - coming soon")


if __name__ == "__main__":
    main()
