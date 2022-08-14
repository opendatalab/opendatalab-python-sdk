#
# Copyright 2022 Shanghai AI Lab. Licensed under MIT License.
#
from opendatalab.cli.utility import ContextInfo, exception_handler


@exception_handler
def _implement_login(obj: ContextInfo, username: str, password: str) -> None:    
    client = obj.get_client()
    odl_api = client.get_api()
    # config_json = odl_api.login(username=username, password=password)
    config_json = odl_api.odl_auth(account=username, password=password)
    obj.update_config(config_json)
    
    print(f"Login Successful as {username}")

