#
# Copyright 2022 Shanghai AI Lab. Licensed under MIT License.
#
from opendatalab.cli.utility import ContextInfo, exception_handler
from opendatalab.client.client import Client


@exception_handler
def _implement_search(obj: ContextInfo, dataset: str) -> None:
    
    client = obj.get_client()
    odl_api = client.get_api()
    odl_api.search_dataset(dataset)
