#!/usr/bin/env python3
#
# Copyright 2022 Shanghai AI Lab. Licensed under MIT License.
#

"""OpenDataLab CLI utility functions."""
import json
import sys
from functools import wraps
from typing import Any, Callable, TypeVar

import click
from rich import print as rprint

from opendatalab.__version__ import __version__
from opendatalab.cli.config import config as client_config
from opendatalab.client import Client
from opendatalab.exception import OpenDataLabError
from opendatalab.utils import UUID

_Callable = TypeVar("_Callable", bound=Callable[..., None])


class ContextInfo:
    """This class contains command context."""

    def __init__(self, url: str, token: str):
        self.url = url
        self.token = token
        self.config = client_config
        self.conf_file = client_config._get_config_filepath()
        self._conf_content = self.check_config()
        odl_cookie = self._conf_content['user.token'] if self._conf_content['user.token'] else ""
        self.cookie = odl_cookie

        self.check_ret = 0
        self.install_version = __version__
        self.latest_version = None
        self.warning = "[red]WARNING[/red]:This CLI tool is deprecated and will be removed in a future release.\nThe [bold yellow]opendatalab(odl)[/bold yellow] pkg has been deprecated and will no longer be supported in few weeks.\nWe recommend that you switch to the [bold yellow]openxlab[/bold yellow] pkg, which accept same username/password,\nprovides the same functionality and other enhanced AI friendly features.\nMore details please refer to [blue]https://openxlab.org.cn/datasets[/blue]\n"
        rprint(self.warning)

    def get_client(self) -> Client:
        return Client(self.url, self.token, self.cookie)

    def get_content(self):
        return self._conf_content

    def set_content(self, content: dict) -> None:
        for key, value in content.items():
            self._conf_content[key] = value

            if key == 'user.token' and not content[key]:
                self.cookie = content[key]

    def get_config_content(self):
        try:
            with open(self.conf_file, 'r') as f:
                config_content = json.load(f)
        except json.decoder.JSONDecodeError:
            config_content = {}

        return config_content

    def check_config(self):
        res = self.get_config_content()
        if not res:
            init_config_dict = {
                'endpoint': self.url,
                'user.email': '',
                'user.token': '',
                'odl_anonymous': UUID,
            }
            result = init_config_dict
            with open(self.conf_file, 'w') as f:
                json.dump(init_config_dict, f, indent=4, sort_keys=True, separators=(',', ':'))
        else:
            result = res

        return result

    def update_config(self, content: dict) -> None:
        res = self.get_config_content()
        if res:
            self.set_content(content)
            with open(self.conf_file, 'w') as f:
                f.seek(0)
                json.dump(self._conf_content, f, indent=4, sort_keys=True, separators=(',', ':'))

    def clean_config(self):
        res = self.get_config_content()
        if not res:
            self.check_config()
        else:
            with open(self.conf_file, "w") as f:
                if 'user.token' in res.keys():
                    res['user.token'] = ''
                if 'user.email' in res.keys():
                    res['user.email'] = ''
                f.seek(0)
                json.dump(res, f, indent=4, sort_keys=True, separators=(',', ':'))

        return res

    def set_check_info(self, latest_version, check_ret):
        self.latest_version = latest_version
        self.check_ret = check_ret

    def get_check_ret(self):
        return self.check_ret


def implement_cli(ctx: click.Context, url: str, token: str) -> None:
    ctx.obj = ContextInfo(url, token)
    # ctx.obj.check_config()


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
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            func(*args, **kwargs)
        except OpenDataLabError as err:
            if err.STATUS_CODE == 401:
                click.secho(f"Error: authentication failure, please login!", err=True, fg='red')
                pass
            elif err.STATUS_CODE == 403:
                click.secho(f"Unable to access. Please visit the dataset homepage!", err=True, fg='red')
                pass
            elif err.STATUS_CODE == 404:
                click.secho(f"Data not exists!", err=True, fg='red')
                pass
            elif err.STATUS_CODE == 412:
                click.secho(f"Access with cdn error!", err=True, fg='red')
                pass
            elif err.STATUS_CODE == 500:
                click.secho(f"Internal server occurs!", err=True, fg='red')
                pass
            else:
                click.secho(f"Error occurs!!!", err=True, fg='red')

            sys.exit(1)

    return wrapper  # type: ignore[return-value]
