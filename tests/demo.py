import json

from opendatalab.__version__ import __url__
from opendatalab.cli.get import implement_get
from opendatalab.cli.info import implement_info
from opendatalab.cli.login import implement_login
from opendatalab.cli.ls import implement_ls
from opendatalab.cli.search import implement_search
from opendatalab.cli.utility import ContextInfo

if __name__ == '__main__':
    """
    ContextInfo: default
        please use shell login first, use: opendatalab login
    """
    ctx = ContextInfo(__url__, "")
    client = ctx.get_client()
    odl_api = client.get_api()

    # 0. login with account
    # account = "xxxxx"  # your username
    # pw = "xxxxx"  # your password
    # print(f'*****'*8)
    # implement_login(ctx, account, pw)

    # 1. search demo    
    res_list = odl_api.search_dataset("coco")
    # for index, res in enumerate(res_list):
    #     print(f"-->index: {index}, result: {res['name']}")

    # implement_search("coco")
    print(f'*****'*8)

    # 2. list demo
    implement_ls(ctx, 'TAO')
    print(f'*****' * 8)

    # 3. read file online demo
    dataset = client.get_dataset('FB15k')
    with dataset.get('meta/info.json', compressed=False) as fd:
        content = json.load(fd)
        print(f"{content}")
    print(f'*****'*8)

    # 4. get dataset info
    implement_info(ctx, 'FB15k')

    # 5. download
    # get all files of dataset
    # implement_get(ctx, "MNIST", 4, 0)

    # get partial files of dataset
    implement_get(ctx, "GOT-10k/data/test_data.zip", 4, 0) # 139, zip 1.16G GOT-10k
    print(f'*****' * 5)
