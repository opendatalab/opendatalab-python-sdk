import json
import pytest
from opendatalab.cli.ls import _implement_ls
from opendatalab.cli.info import _implement_info
from opendatalab.cli.utility import ContextInfo
from opendatalab.client.api import OpenDataLabAPI
from opendatalab.__version__ import __url__

    
if __name__ == '__main__':
    """
    ContextInfo: default
        please use shell login first, use: opendatalab login
    """
    ctx = ContextInfo(__url__, "")
    client = ctx.get_client()
    odl_api = client.get_api()

    # 1. search demo    
    res_list = odl_api.search_dataset("coco")
    for index, res in enumerate(res_list):
        print(f"-->index: {index}, result: {res['name']}")
    print(f'*****'*5)   
    
    # 2. list demo
    _implement_ls(ctx, 'FB15k')
    print(f'*****'*5)   
    
    # 3. read file demo 
    dataset = client.get_dataset('FB15k') 
    with dataset.get('data_info/info.json', compressed=False) as fd:
        content = json.load(fd)
        print(f"{content}")    
    print(f'*****'*5)
    
    # 4. get dataset info
    _implement_info(ctx, 'FB15k')
    print(f'*****'*5)

    
