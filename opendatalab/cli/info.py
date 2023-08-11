#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2022 Shanghai AI Lab. Licensed under MIT License.
#
from rich import box
from rich.console import Console
from rich.table import Table

from opendatalab.cli.utility import ContextInfo, exception_handler
from opendatalab.utils import bytes2human


def _format_types(info_data, type_name):
    types_str = ""
    if type_name in info_data['attrs'].keys():
        types_list = info_data['attrs'][type_name]
        if types_list and len(types_list) > 0:
            types_str = ", ".join([x['name']['en'] for x in types_list])

    return types_str


def reformat_info_data(info_data):
    license_str = _format_types(info_data, 'license')
    publisher_str = _format_types(info_data, 'publisher')
    media_types_str = _format_types(info_data, 'mediaTypes')
    label_types_str = _format_types(info_data, 'labelTypes')
    task_types_str = _format_types(info_data, 'taskTypes')
    tags_str = _format_types(info_data, 'tags')

    data_introduction = info_data['introduction']['en']
    introduction_str = ""
    if data_introduction and len(data_introduction) > 0:
        introduction_str = data_introduction[:97] + '...'

    citation_data = info_data['attrs']['citation']
    citation_str = ""
    if citation_data and len(citation_data) > 0:
        citation_str = citation_data.strip("```").replace('\r', '').replace('\n', '')

    similar_data_list = info_data['similar']
    similar_ds_str = ""
    if similar_data_list and len(similar_data_list) > 0:
        similar_ds_str = ", ".join([x['name'] for x in similar_data_list])

    info_data_result = {
        'Name': info_data['name'],
        'File Bytes': str(bytes2human(info_data['attrs']['fileBytes'])),
        'File Count': str(info_data['attrs']['fileCount']),
        'Introduction': introduction_str,
        'Issue Time': info_data['attrs']['publishDate'],
        'License': license_str,
        'Author': publisher_str,
        'Data Type': media_types_str,
        'Label Type': label_types_str,
        'Task Type': task_types_str,
        'Tags': tags_str,
        'HomePage': info_data['attrs']['publishUrl'],
        'Citation': citation_str,
        'Similar Datasets': similar_ds_str,
    }

    return info_data_result


@exception_handler
def implement_info(obj: ContextInfo, dataset: str) -> None:
    """
    implement for displaying dataset info
    Args:
        obj (ContextInfo): context object
        dataset (str): dataset name

    Returns:

    """
    client = obj.get_client()
    odl_api = client.get_api()
    info_data = odl_api.get_info(dataset)

    info_data_result = reformat_info_data(info_data)
    console = Console()
    table = Table(show_header=True, header_style='bold cyan', box=box.ASCII2)
    table.add_column("Field", width=20, justify='full', overflow='fold')
    table.add_column("Content", width=120, justify='full', overflow='fold')

    for key in info_data_result.keys():
        val = info_data_result[key]
        val = "" if not val else val
        table.add_row(key, val, end_section=True)

    console.print(table)
