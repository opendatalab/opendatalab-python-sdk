#
# Copyright 2022 Shanghai AI Lab. Licensed under MIT License.
#
import sys

from rich import box
from rich import print as rprint
from rich.console import Console
from rich.table import Table

from opendatalab.cli.utility import ContextInfo, exception_handler
from opendatalab.exception import OdlAccessDeniedError
from opendatalab.utils import bytes2human


@exception_handler
def implement_ls(obj: ContextInfo, dataset: str):
    """
    implementation for show dataset files
    Args:
        obj (ContextInfo):
        dataset (str): dataset name

    Returns:

    """
    ds_split = dataset.split("/")
    if len(ds_split) > 1:
        dataset_name = ds_split[0]
        sub_dir = "/".join(ds_split[1:])
    else:
        dataset_name = dataset
        sub_dir = ""

    client = obj.get_client()
    info_dataset_name = client.get_api().get_info(dataset_name)['name']
    dataset_instance = client.get_dataset(dataset_name=info_dataset_name)

    dataset_res_dict = client.get_api().get_dataset_files(dataset_name=info_dataset_name, prefix = sub_dir)
    
    # generate output info dict
    object_info_dict = {}
    total_files, total_size = 0, 0
    total_files = dataset_res_dict['total']
    for info in dataset_res_dict['list']:
        object_info_dict[info['path']] = bytes2human(info['size'])
        total_size += info['size']


    if len(object_info_dict) == 0:
        raise OdlAccessDeniedError()
        sys.exit(-1)

    sorted_object_info_dict = dict(sorted(object_info_dict.items(), key=lambda x: x[0], reverse=True))

    console = Console()
    table = Table(show_header=True, header_style='bold cyan', box=box.ASCII2)  # ROUNDED
    table.add_column("File Name", min_width=20, justify='left')
    table.add_column("Size", width=12, justify='left')

    print(f"Total file count: {total_files}, Size: {bytes2human(total_size)}")
    for key, val in sorted_object_info_dict.items():
        table.add_row(key, val, end_section=True)
    console.print(table)
