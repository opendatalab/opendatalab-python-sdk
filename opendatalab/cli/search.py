#
# Copyright 2022 Shanghai AI Lab. Licensed under MIT License.
#
import re
from rich import box
from rich.console import Console
from rich.table import Table
from opendatalab.cli.utility import ContextInfo, exception_handler
from opendatalab.utils import bytes2human


def rich_content_str(keywords: str, content: str):
    keywords = keywords.strip()
    len_keywords = len(keywords)
    hl_prefix = '[bold magenta]'
    hl_suffix = '[/bold magenta]'
    start_index_list = [m.start() for m in re.finditer(keywords.lower(), content.lower())]
    result = []
    curs = 0
    if start_index_list and len(start_index_list) > 0:
        for i in start_index_list:
            result.append(content[curs:i])
            result.append(hl_prefix)
            result.append(content[i: i + len_keywords])
            result.append(hl_suffix)
            curs = i + len_keywords

        if curs < len(content):
            result.append(content[curs:])

    rich_result = ''.join(result)
    if not rich_result:
        rich_result = content

    return rich_result


@exception_handler
def implement_search(obj: ContextInfo, keywords: str) -> None:
    """
    implement dataset search through backend api
    Args:
        obj (ContextInfo):
        keywords (str):

    Returns:

    """
    client = obj.get_client()
    odl_api = client.get_api()
    result_list = odl_api.search_dataset(keywords)

    console = Console()
    table = Table(show_header=True, header_style='bold cyan', box=box.ASCII2)
    table.add_column("Name", min_width=10, justify='left', overflow='fold')
    table.add_column("DataType", min_width=8, justify='left', overflow='fold')
    table.add_column("FileByte", min_width=8, overflow='fold')
    table.add_column("FileCount", min_width=8, overflow='fold')
    table.add_column("TaskType", min_width=8, justify='left', overflow='fold')
    table.add_column("LabelType", min_width=8, justify='left', overflow='fold')
    table.add_column("ViewCount", min_width=8, justify='left', overflow='fold')
    table.add_column("Introduction", min_width=20, justify='left', overflow='fold')

    # TODO:
    if result_list:
        for _, res in enumerate(result_list):
            ds_name = res['name']
            ds_name_rich = rich_content_str(keywords=keywords, content=ds_name)
            ds_data_types = ','.join([dmt['name'] for dmt in res['mediaTypes']])
            ds_file_byte = bytes2human(res['fileBytes'])
            ds_file_count = res['fileCount']
            ds_task_types = ','.join([dtt['name'] for dtt in res['taskTypes']])
            ds_task_types_rich = rich_content_str(keywords=keywords, content=ds_task_types)
            ds_label_types = ','.join([dlt['name'] for dlt in res['labelTypes']])
            ds_label_types_rich = rich_content_str(keywords=keywords, content=ds_label_types)
            ds_view_count = res['viewCount']
            ds_desc = res['introductionText'][:97] + '...'
            ds_desc_rich = rich_content_str(keywords=keywords, content=ds_desc)

            table.add_row(ds_name_rich, ds_data_types, str(ds_file_byte), str(ds_file_count), ds_task_types_rich,
                          ds_label_types_rich, str(ds_view_count), ds_desc_rich, end_section=True)

    console.print(table)