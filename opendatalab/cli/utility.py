#!/usr/bin/env python3
#
# Copyright 2022 Shanghai AI Lab. Licensed under MIT License.
#

"""OpenDataLab CLI utility functions."""
import sys
import json
from functools import wraps
from typing import Any, Callable, TypeVar

import click

from opendatalab.cli.config import config as client_config
from opendatalab.client.client import Client
from opendatalab.exception import OpenDataLabError, OpenDataLabInternalError

_Callable = TypeVar("_Callable", bound=Callable[..., None])


class ContextInfo:
    """This class contains command context."""

    def __init__(self, url: str, token: str):
        self.url = url
        self.token = token
        self.config = client_config
        self.conf_file = client_config._get_config_filepath()
        self._conf_content = {} 
    
    def get_client(self) -> Client:
        return Client(self.url, self.token)
    
    def get_content(self):
        return self._conf_content
    
    def set_content(self, content: dict) -> None:
        for key, value in content.items():
            self._conf_content[key] = value
            
    def get_config_content(self):
        try:
            with open(self.conf_file, 'r') as jf:
                config_content = json.load(jf)
        except json.decoder.JSONDecodeError:
            config_content = {}
        
        return config_content
    
    def update_config(self, content: dict) -> None:
        with open(self.conf_file, 'w') as jf:
            lines = jf.readlines()
            json.dump(content, jf)
            self.set_content(content)
    
    def clean_config(self):
        self.config.clean_config()
        self._conf_content = {}
        
            
def _implement_cli(ctx: click.Context, url: str, token: str) -> None:
    ctx.obj = ContextInfo(url, token)
    conf_content = {
                'endpoint': url,
                'user.email': "",
                'user.token': "",
                }
    # ctx.obj.update_config(conf_content)


def error(message: str):
    """Print the error message and exit the program.

    Arguments:
        message: The error message to echo.

    """
    click.secho(f"ERROR: {message}", err=True, fg="red")
    sys.exit(1)


def exception_handler(func: _Callable) -> _Callable:
    """Decorator for CLI functions to catch custom exceptions.

    Arguments:
        func: The CLI function needs to be decorated.

    Returns:
        The CLI function with exception catching procedure.

    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> None:
        try:
            func(*args, **kwargs)
        except OpenDataLabInternalError as err:
            print(err)
            raise
        except OpenDataLabError as err:
            error(str(err))

    return wrapper  # type: ignore[return-value]