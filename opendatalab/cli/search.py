#
# Copyright 2022 Shanghai AI Lab. Licensed under MIT License.
#
from opendatalab.cli.utility import ContextInfo, exception_handler
from opendatalab.client.client import Client
from opendatalab.utils import bytes2human

from rich.console import Console
from rich.table import Table
import re


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
            result.append(content[i : i + len_keywords])
            result.append(hl_suffix)
            curs = i + len_keywords

        if curs < len(content):
            result.append(content[curs:])
    
    rich_result = ''.join(result)
    if not rich_result:
        rich_result = content

    return rich_result


@exception_handler
def _implement_search(obj: ContextInfo, keywords: str) -> None:
    
    client = obj.get_client()
    odl_api = client.get_api()
    result_list = odl_api.search_dataset(keywords)

    # rprint('{:<30}{:<10}{:<100}\t{:<10}\n'.format('Name', 'FileSize', 'Description', 'DownloadCount'))
    console = Console()
    table = Table(show_header=True, header_style='bold cyan')
    table.add_column("Name", style="dim", justify='left')
    table.add_column("FileSize", style="dim", width=10)
    table.add_column("Description", justify='full')
    table.add_column("DownloadCount", width=20, justify='right')

    if result_list:
        for _, res in enumerate(result_list):
            ds_name = res['name']
            ds_name_rich = rich_content_str(keywords=keywords, content=ds_name)

            ds_desc = res['introductionText']
            ds_desc_rich = rich_content_str(keywords=keywords, content=ds_desc)

            ds_dw_cnt = res['downloadCount']
            ds_file_bytes = bytes2human(res['fileBytes'])
            table.add_row(ds_name_rich, str(ds_file_bytes), ds_desc_rich, str(ds_dw_cnt))

            # rprint('{:<30}{:<10}{:<100}\t{:<10}\n'.format(ds_name_rich, ds_file_bytes, ds_desc_rich, ds_dw_cnt))
    console.print(table)

if __name__ == '__main__':
    console = Console()
    table = Table(show_header=True, header_style='bold cyan')
    table.add_column("Name", style="dim", width=30)
    table.add_column("FileSize", style="dim", width=10)
    table.add_column("Description", justify='left')
    table.add_column("DownloadCount", width=20, justify='right')

    key = 'COCO'
    name = 'Coco-QA'
    contents = 'COCO-QA is a dataset for visual question answering. It consists of'
    ds_name_rich = rich_content_str(key, name)
    ds_desc_rich = rich_content_str(key, contents)
    
    table.add_row(ds_name_rich, '28.2K', ds_desc_rich, str(100))

    # rprint('{:<30}{:<10}{:<100}\t{:<10}\n'.format('Name', 'FileSize', 'Description', 'DownloadCount'))
    # rprint('{:<30}{:<10}{:<100}\t{:<10}\n'.format(ds_name_rich, '100 MB', ds_desc_rich, 10))


    key = 'COCO'
    name = 'DeCOCO'
    contents = 'DeCOCO is a bilingual (English-German) corpus of image descriptions, where the English part is ex'
    ds_name_rich = rich_content_str(key, name)
    ds_desc_rich = rich_content_str(key, contents)
    table.add_row(ds_name_rich, '28.2K', ds_desc_rich, str(10))

    # rprint('{:<30}{:<10}{:<100}\t{:<10}\n'.format('Name', 'FileSize', 'Description', 'DownloadCount'))
    # rprint('{:<30}{:<10}{:<100}\t{:<10}\n'.format(ds_name_rich, '100 MB', ds_desc_rich, 10))

    key = 'coco'
    name = 'COCO_2017_Instance'
    contents = 'COCO is a large-scale object detection, segmentation, and captioning dataset. COCO has several fe'
    ds_name_rich = rich_content_str(key, name)
    ds_desc_rich = rich_content_str(key, contents)
    table.add_row(ds_name_rich, '28.2K', ds_desc_rich, str(0))

    # rprint('{:<30}{:<10}{:<100}\t{:<10}\n'.format('Name', 'FileSize', 'Description', 'DownloadCount'))
    # rprint('{:<30}{:<10}{:<100}\t{:<10}\n'.format(ds_name_rich, '100 MB', ds_desc_rich, 10))
    
    console.print(table)