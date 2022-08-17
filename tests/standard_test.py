import click

from click.testing import CliRunner
from opendatalab.cli import cmd


def test_cli():
    result = CliRunner.invoke(cmd.cli.commands, ['--version'])
    assert result.exit_code == 0
    print(f"ret: {result.output}")
