#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. currentmodule:: test_cli
.. moduleauthor:: evil.unicorn1 <evil.unicorn1@gmail.com>

This is the test module for the project's command-line interface (CLI)
module.
"""
# fmt: off
import chatbot_server.cli as cli
from chatbot_server import __version__
# fmt: on
from click.testing import CliRunner, Result


# To learn more about testing Click applications, visit the link below.
# http://click.pocoo.org/5/testing/


def test_version_displays_library_version():
    """
    Arrange/Act: Run the `version` subcommand.
    Assert: The output matches the library version.
    """
    runner: CliRunner = CliRunner()
    result: Result = runner.invoke(cli.cli, ["version"])
    assert (
        __version__ in result.output.strip()
    ), "Version number should match library version."
