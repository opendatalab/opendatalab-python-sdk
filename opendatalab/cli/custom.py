#!/usr/bin/env python3
#
# Copyright 2022 Shanghai AI Lab. Licensed under MIT License.
#
"""Customization of the click classes for OpenDataLab CLI."""

from typing import Any
import click


class CustomCommand(click.Command):
    """Wrapper class of ``click.Command`` for CLI commands with custom help.

    Arguments:
        kwargs: The keyword arguments pass to ``click.Command``.

    """

    def __init__(self, **kwargs: Any) -> None:
        self.synopsis = kwargs.pop("synopsis", ())
        super().__init__(**kwargs)

    def format_help(self, ctx: click.Context, formatter: click.HelpFormatter) -> None:
        """Writes the custom help into the formatter if it exists.

        Override the original ``click.Command.format_help`` method by
        adding :meth:`CustomCommand.format_synopsis` to form custom help message.

        Arguments:
            ctx: The context of the command.
            formatter: The help formatter of the command.

        """
        formatter.width = 100
        self.format_usage(ctx, formatter)
        self.format_help_text(ctx, formatter)
        self.format_synopsis(formatter)
        self.format_options(ctx, formatter)
        self.format_epilog(ctx, formatter)

    def format_synopsis(self, formatter: click.HelpFormatter) -> None:
        """Write the synopsis to the formatter if exists.

        Arguments:
            formatter: The help formatter of the command.
        """
        if not self.synopsis:
            return

        with formatter.section("Synopsis"):
            for example in self.synopsis:
                formatter.write_text(example)
