#
# Copyright 2022 Shanghai AI Lab. Licensed under MIT License.
#
from opendatalab.cli.utility import ContextInfo, exception_handler
from opendatalab.client.client import Client
from opendatalab.utils import bytes2human


@exception_handler
def _implement_search(obj: ContextInfo, dataset: str) -> None:
    
    client = obj.get_client()
    odl_api = client.get_api()
    result_list = odl_api.search_dataset(dataset)
    print('{:<10}{:<30}{:<10}{:<100}\t{:<10}'.format('Index', 'Name', 'FileSize', 'Description', 'DownloadCount'))

    if result_list:
        for i, res in enumerate(result_list):
            index = i
            ds_name = res['name']
            ds_desc = res['introductionText'][:97] + '...'
            ds_dw_cnt = res['downloadCount']
            ds_file_bytes = bytes2human(res['fileBytes'])
            print('{:<10}{:<30}{:<10}{:<100}\t{:<10}'.format(index, ds_name, ds_file_bytes, ds_desc, ds_dw_cnt))