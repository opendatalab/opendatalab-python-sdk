#
# Copyright 2022 Shanghai AI Lab. Licensed under MIT License.
#
from opendatalab.cli.utility import ContextInfo, exception_handler
from opendatalab.client.client import Client
from opendatalab.utils import bytes2human

from rich import print as rprint
import re


def rich_content_str(keywords: str, content: str):
    result = []
    keywords = keywords.strip()
    len_keywords = len(keywords)
    hl_prefix = '[bold magenta]'
    hl_suffix = '[/bold magenta]'

    # print(f"keywords: {keywords}, content: {content}")
    start_index_list = [m.start() for m in re.finditer(keywords.lower(), content.lower())]
    # print(f"start_index: {start_index_list}")

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
    # print(f"rich_result: {rich_result}")

    return rich_result


@exception_handler
def _implement_search(obj: ContextInfo, keywords: str) -> None:
    
    client = obj.get_client()
    odl_api = client.get_api()
    result_list = odl_api.search_dataset(keywords)

    rprint('{:<30}{:<10}{:<100}\t{:<10}'.format('Name', 'FileSize', 'Description', 'DownloadCount'))


    if result_list:
        for _, res in enumerate(result_list):
            ds_name = res['name']
            ds_name_rich = rich_content_str(keywords=keywords, content=ds_name)

            ds_desc = res['introductionText'][:97] + '...'
            ds_desc_rich = rich_content_str(keywords=keywords, content=ds_desc)

            ds_dw_cnt = res['downloadCount']
            ds_file_bytes = bytes2human(res['fileBytes'])

            rprint('{:<30}{:<10}{:<100}\t{:<10}'.format(ds_name_rich, ds_file_bytes, ds_desc_rich, ds_dw_cnt))


# if __name__ == '__main__':
#     key = 'COCO'
#     name = 'Coco-QA'
#     contents = 'COCO-QA is a dataset for visual question answering. It consists of'
#     ds_name_rich = rich_content_str(key, name)
#     ds_desc_rich = rich_content_str(key, contents)

#     rprint('{:<30}{:<10}{:<100}\t{:<10}'.format('Name', 'FileSize', 'Description', 'DownloadCount'))
#     rprint('{:<30}{:<10}{:<100}\t{:<10}'.format(ds_name_rich, '100 MB', ds_desc_rich, 10))


#     key = 'COCO'
#     name = 'DeCOCO'
#     contents = 'DeCOCO is a bilingual (English-German) corpus of image descriptions, where the English part is ex'
#     ds_name_rich = rich_content_str(key, name)
#     ds_desc_rich = rich_content_str(key, contents)

#     rprint('{:<30}{:<10}{:<100}\t{:<10}'.format('Name', 'FileSize', 'Description', 'DownloadCount'))
#     rprint('{:<30}{:<10}{:<100}\t{:<10}'.format(ds_name_rich, '100 MB', ds_desc_rich, 10))

#     key = 'coco'
#     name = 'COCO_2017_Instance'
#     contents = 'COCO is a large-scale object detection, segmentation, and captioning dataset. COCO has several fe'
#     ds_name_rich = rich_content_str(key, name)
#     ds_desc_rich = rich_content_str(key, contents)

#     rprint('{:<30}{:<10}{:<100}\t{:<10}'.format('Name', 'FileSize', 'Description', 'DownloadCount'))
#     rprint('{:<30}{:<10}{:<100}\t{:<10}'.format(ds_name_rich, '100 MB', ds_desc_rich, 10))