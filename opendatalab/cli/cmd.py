#
# Copyright 2022 Shanghai AI Lab. Licensed under MIT License.
#

"""Definitions of OpenDataLab Command-line Interface commands."""

from functools import partial
import click

from opendatalab.__version__ import __version__
from opendatalab.cli.custom import CustomCommand
from opendatalab.cli.utility import ContextInfo

@click.group(context_settings={"help_option_names": ("-h", "--help")})
@click.version_option(__version__)
@click.option("-u", "--url", type=str, default="https://opendatalab-ut.shlab.tech", help="The login url.", hidden=True) 
@click.option("-t", "--token", type=str, default="", help="OpenDatalab user api token", hidden=True, envvar="OPENDATALAB-API-TOKEN",)
@click.pass_context
def cli(ctx: click.Context, url: str, token: str) -> None:
    """You can use `opendatalab <command>` to access open datasets.\f

    Arguments:
        ctx: The context to be passed as the first argument.
        url: The login URL.
    """
    # ctx.ensure_object(dict)
    
    from opendatalab.cli.utility import _implement_cli
    _implement_cli(ctx, url, token)
    
command = partial(cli.command, cls=CustomCommand)

@command(
    synopsis=(
        "$ opendatalab version      # show opendatalab version.",
    )
)
def version():
    """Show opendatalab version.
    """
    click.echo(f"opendatalab, {__version__}")
    

@command(
    synopsis=(
        "$ opendatalab logout      # logout current account",
    )
)
@click.pass_obj
def logout(obj: ContextInfo):
    """Logout opendatalab account.\f

    Args:
        obj (ContextInfo): context info
    """
    from opendatalab.cli.logout import _implement_logout
    _implement_logout(obj)
            
    
@command(
    synopsis=(
        "$ opendatalab login -u -p      # login opendatalab with username and password",
    )
)
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
    default="", help="Password for opendatalab."
)
@click.pass_obj
def login(obj: ContextInfo, username: str, password: str):
    """Login opendatalab with account.\f

    Args:
        obj (ContextInfo): context info
        username (str): account username
        password (str): account password
    """
    from opendatalab.cli.login import _implement_login
    _implement_login(obj, username, password)
    

@command(
    synopsis=(
        "$ opendatalab ls dataset              # list dataset files.",
        "$ opendatalab ls dataset/sub_dir      # list dataset/sub_dir files.",
    )
)
@click.argument("name", nargs=1)
@click.pass_obj
def ls(obj: ContextInfo, name: str) -> None:
    """List files of the dataset.\f

    Args:
        obj (ContextInfo): context info
        name (str): dataset name
    """
    from opendatalab.cli.ls import _implement_ls
    _implement_ls(obj, name)
    

@command(
    synopsis=(
        "$ opendatalab search keywords      # search dataset with keywords.",
    )
)
@click.argument("keywords", nargs=1)
@click.pass_obj
def search(obj: ContextInfo, keywords):
    """Search dataset info.\f

    Args:
        obj (ContextInfo): context info
        keywords (str): dataset keywords
    """
    from opendatalab.cli.search import _implement_search

    _implement_search(obj, keywords)
    

@command(
    synopsis=(
        "$ opendatalab info dataset_name      # show dataset info.",
    )
)
@click.argument("name", nargs=1)
@click.pass_obj
def info(obj: ContextInfo, name):
    """Print dataset info.\f

    Args:
        obj (ContextInfo): context info
        name (str): dataset name
    """
    from opendatalab.cli.info import _implement_info
    _implement_info(obj, name)
    
    
@command(
    synopsis=(
        "$ opendatalab get dataset_name      # get dataset files into local.",
    )
)
@click.argument("name", nargs=1)
@click.option(
    "--thread",
    "-t",
    default=10,
    help="Number of thread for download",
    show_default=True,
)
@click.option(
    "--limit_speed",
    default=0,
    help="Download limit speed: KB/s, 0 is unlimited",
    show_default=True,
)
@click.pass_obj
def get(obj: ContextInfo, name, thread, limit_speed):
    """Get(Download) dataset files into local path.\f

    Args:
        obj (ContextInfo): context info\f
        name (str): dataset name\f
        thread (int): multil-thread number\f
        limit_speed (int): limit download speed, for not limit set value to 0
    """    
    from opendatalab.cli.get import _implement_get
    _implement_get(obj, name, thread, limit_speed)


if __name__ == "__main__":
    cli()