#
# Copyright 2022 Shanghai AI Lab. Licensed under MIT License.
#

"""Definitions of OpenDataLab Command-line Interface commands."""
import sys
from functools import partial

import click

from opendatalab.__version__ import __svc__, __url__, __version__
from opendatalab.cli.custom import CustomCommand
from opendatalab.cli.utility import ContextInfo


@click.group(context_settings={"help_option_names": ("-h", "--help")})
@click.version_option(__version__)
@click.option("-u", "--url", type=str, default=__url__, help="The login url.", hidden=True)
@click.option("-t", "--token", type=str, default="", help="odl api token", hidden=True,
              envvar="OPENDATALAB-API-TOKEN", )
@click.pass_context
def cli(ctx: click.Context, url: str, token: str) -> None:
    """You can use `odl <command>` to access open datasets.\f

    Arguments:
        token:
        ctx: The context to be passed as the first argument.
        url: The login URL.
    """
    # ctx.ensure_object(dict)
    from opendatalab.cli.utility import implement_cli
    implement_cli(ctx, url, token)
    upgrade(ctx.obj)


command = partial(cli.command, cls=CustomCommand)


@command(synopsis=("$ odl version     # show opendatalab version",))
def version():
    """Show opendatalab version.
    """
    click.echo(f"odl version, current: {__version__}, svc: {__svc__}")


# @command(synopsis=("$ odl upgrade      # check opendatalab version upgrade.",))
# @click.pass_obj
def upgrade(obj: ContextInfo):
    """upgrade opendatalab version.
    """
    from opendatalab.cli.upgrade import implement_upgrade
    implement_upgrade(obj)


@command(synopsis=("$ odl logout      # logout current account",))
@click.pass_obj
def logout(obj: ContextInfo):
    """Logout opendatalab account.\f
    Args:
        obj (ContextInfo): context info
    """
    from opendatalab.cli.logout import implement_logout
    implement_logout(obj)


@command(synopsis=("$ odl login -u -p      # login opendatalab",))
@click.option(
    "-u",
    "--username",
    prompt="Username",
    default="",
    help="Username for opendatalab",
)
@click.option(
    "-p",
    "--password",
    prompt="Password",
    hide_input=True,
    default="", help="Password for opendatalab"
)
@click.pass_obj
def login(obj: ContextInfo, username: str, password: str):
    """Login opendatalab with account.\f

    Args:
        obj (ContextInfo): context info
        username (str): account username
        password (str): account password
    """
    from opendatalab.cli.login import implement_login
    implement_login(obj, username, password)


@command(synopsis=("$ odl ls dataset              # list dataset files",))
@click.argument("name", nargs=1)
@click.pass_obj
def ls(obj: ContextInfo, name: str) -> None:
    """List files of the dataset.\f

    Args:
        obj (ContextInfo): context info
        name (str): dataset name
    """
    from opendatalab.cli.ls import implement_ls
    implement_ls(obj, name)


@command(synopsis=("$ odl search keywords      # search dataset with keywords",))
@click.argument("keywords", nargs=1)
@click.pass_obj
def search(obj: ContextInfo, keywords):
    """Search dataset info.\f

    Args:
        obj (ContextInfo): context info
        keywords (str): dataset keywords
    """
    from opendatalab.cli.search import implement_search
    implement_search(obj, keywords)


@command(synopsis=("$ odl info dataset_name      # show dataset info",))
@click.argument("name", nargs=1)
@click.pass_obj
def info(obj: ContextInfo, name):
    """Print dataset info.\f
    Args:
        obj (ContextInfo): context info
        name (str): dataset name
    """
    from opendatalab.cli.info import implement_info
    implement_info(obj, name)


@command(synopsis=("$ odl get dataset_name      # get dataset files into local",))
@click.argument("name", nargs=1)
@click.option(
    "--dest",
    "-d",
    default='',
    help="Desired dataset store path",
    show_default=True
)
@click.option(
    "--workers",
    "-w",
    default = 8,
    help= "number of workers",
    show_default = True
)
@click.pass_obj
def get(obj: ContextInfo, name, dest, workers):
    """Get(Download) dataset files into local path.\f
    Args:
        obj (ContextInfo): context info\f
        name (str): dataset name\f
        destination(str): desired dataset store path\f
        wokers(str): number of workers\f
    """
    
    from opendatalab.cli.get import implement_get
    implement_get(obj, name, dest, workers)
if __name__ == "__main__":
    cli()
