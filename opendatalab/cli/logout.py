#
# Copyright 2022 Shanghai AI Lab. Licensed under MIT License.
#
from opendatalab.cli.utility import ContextInfo, exception_handler
import click


@exception_handler
def _implement_logout(obj: ContextInfo) -> None:
    
    #TODO: bugfix, config_content seems not update even config changes
    config_content = obj.get_config_content()
    print(f"config_content: {config_content}")
    username = ""
    if 'user.email' in config_content.keys():
        username = config_content['user.email']
    
    if username.strip():
        if click.confirm('Do you want to logout?'):
            print(f"{username} Logged Out")
            obj.clean_config()
    else:
        print("Warning: You haven't logined, please login first.")
