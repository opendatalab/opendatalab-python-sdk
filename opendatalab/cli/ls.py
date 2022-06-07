#
# Copyright 2022 Shanghai AI Lab. Licensed under MIT License.
#
from opendatalab.cli.utility import ContextInfo, exception_handler
from opendatalab.client.client import Client


@exception_handler
def _implement_ls(obj: ContextInfo, dataset: str) -> None:
    
    client = obj.get_client()
    client.get_dataset(dataset)
