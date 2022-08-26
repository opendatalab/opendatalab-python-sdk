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
    similar_data_list = odl_api.get_similar_dataset(dataset)

    data_introd = info_data['introduction']
    introduction_str = ""
    if data_introd and len(data_introd) > 0:
        introduction_str = data_introd[:97] + '...'

    license_list = info_data['licenses']
    license_str = ""
    if license_list and len(license_list) > 0:
        license_str = ", ".join([x['name'] for x in license_list])

    publisher_list = info_data['publisher']
    publisher_str = ""
    if publisher_list and len(publisher_list) > 0:
        publisher_str = ", ".join([x['name'] for x in publisher_list])

    media_types_list = info_data['mediaTypes']
    media_types_str = ""
    if media_types_list and len(media_types_list) > 0:
        media_types_str = ", ".join([x['name'] for x in media_types_list])

    label_types_list = info_data['labelTypes']
    label_types_str = ""
    if label_types_list and len(label_types_list) > 0:
        label_types_str = ", ".join([x['name'] for x in label_types_list])

    task_types_list = info_data['taskTypes']
    task_types_str = ""
    if label_types_list and len(task_types_list) > 0:
        task_types_str = ", ".join([x['name'] for x in task_types_list])

    tags_list = info_data['tags']
    tags_str = ""
    if tags_list and len(tags_list) > 0:
        tags_str = ", ".join([x['name'] for x in tags_list])

    citation_data = info_data['citation']
    citation_str = ""
    if citation_data and len(citation_data) > 0:
        citation_str = citation_data.strip("```").replace('\r', '').replace('\n', '')

    similar_ds_str = ""
    if similar_data_list and len(similar_data_list) > 0:
        similar_ds_str = ", ".join([x['name'] for x in similar_data_list])

    info_data = {
        'Name': info_data['name'],
        'File Bytes': str(bytes2human(info_data['fileBytes'])),
        'File Count': str(info_data['fileCount']),
        'Introduction': introduction_str,
        'Issue Time': info_data['publishDate'],
        'License': license_str,
        'Author': publisher_str,
        'Data Type': media_types_str,
        'Label Type': label_types_str,
        'Task Type': task_types_str,
        'Tags': tags_str,
        'HomePage': info_data['publishUrl'],
        'Citation': citation_str,
        'Similar Datasets': similar_ds_str,
    }

    console = Console()
    table = Table(show_header=True, header_style='bold cyan', box=box.ASCII2)
    table.add_column("Field", width=20, justify='full', overflow='fold')
    table.add_column("Content", width=120, justify='full', overflow='fold')

    for key in info_data.keys():
        val = info_data[key]
        val = "" if not val else val
        table.add_row(key, val, end_section=True)

    console.print(table)
