#
# Copyright 2022 Shanghai AI Lab. Licensed under MIT License.
#
from opendatalab.cli.utility import ContextInfo, exception_handler
import click


@exception_handler
def implement_logout(obj: ContextInfo) -> None:
    ##TODO: add /api/users/sync/logout
    config_content = obj.get_config_content()
    username = ""
    if 'user.email' in config_content.keys():
        username = config_content['user.email']
    
    if username.strip():
        if click.confirm('Do you want to logout?'):
            print(f"{username} logout")
            obj.clean_config()
    else:
        print("Warning: you haven't login.")
