#
# Copyright 2022 Shanghai AI Lab. Licensed under MIT License.
#
from opendatalab.cli.utility import ContextInfo, exception_handler
from opendatalab.client.client import Client
import click


@exception_handler
def _implement_logout(obj: ContextInfo) -> None:
    
    client = obj.get_client()
    config_content = obj.get_content()
    username = config_content['user.email']
    if username.strip():
        if click.confirm('Do you want to logout?'):
            print(f"{username} Logged Out")
    else:
        print("Warning: You haven't logined, please login first.")
