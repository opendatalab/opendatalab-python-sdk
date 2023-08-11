#
# Copyright 2022 Shanghai AI Lab. Licensed under MIT License.
#
import sys

from opendatalab.cli.utility import ContextInfo, exception_handler


@exception_handler
def implement_login(obj: ContextInfo, username: str, password: str) -> None:
    try:
        client = obj.get_client()
        odl_api = client.get_api()
        config_json = odl_api.odl_auth(account=username, password=password)
        obj.update_config(config_json)

    except Exception as e:
        print(f"Login failure with account {username}")
        sys.exit(-1)

    print(f"Login successfully as {username}")
