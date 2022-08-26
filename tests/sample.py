import json
import pytest

from opendatalab.cli.get import implement_get
from opendatalab.cli.ls import implement_ls
from opendatalab.cli.info import implement_info
from opendatalab.cli.login import implement_login
from opendatalab.cli.upgrade import implement_upgrade
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

    # 0. login with uaa
    account = "191637988@qq.com"  # "191637988@qq.com"  "chenlu@pjlab.org.cn"
    pw = "qq11111111"
    # _implement_login(ctx, account, pw)

    # 1. search demo    
    # res_list = odl_api.search_dataset("coco")
    # for index, res in enumerate(res_list):
    #     print(f"-->index: {index}, result: {res['name']}")
    # print(f'*****'*5)

    # 2. list demo
    # implement_ls(ctx, 'TAO')
    # implement_ls(ctx, "OpenXD-SynBody")
    # implement_ls(ctx, "123")

    print(f'*****' * 5)

    # 3. read file demo 
    # dataset = client.get_dataset('TAPOS')
    # with dataset.get('meta/info.json', compressed=False) as fd:
    #     content = json.load(fd)
    #     print(f"{content}")
    # print(f'*****'*5)

    # 4. get dataset info
    # _implement_info(ctx, 'FB15k')

    # 5. download
    implement_get(ctx, "iiii", 4, 0)  #
    # implement_get(ctx, "MNIST", 4, 0)  #
    implement_ls(ctx, "OpenXD-SynBody", 4, 0)
    implement_get(ctx, "123", 4, 0)  #
    # implement_get(ctx, "TAPOS", 4, 0) # /categories/categories.txt
    # implement_get(ctx, '20-MAD', 4, 0) # 1637
    # implement_get(ctx, "ArCOV-19", 4, 0) # 1666,  zip 109M  pass
    # implement_get(ctx, "TAO/1-TAO_TRAIN.zip", 4, 245760) # 125, zip 2-TAO_VAL.zip 1-TAO_TRAIN.zip

    # implement_get(ctx, "aaaaaa", 4, 0)

    # implement_get(ctx, "openlane", 4, 0)
    # implement_get(ctx, 'FB15k', 4, 0) # 84, zip 17.4M pass
    # implement_get(ctx, "GOT-10k/data/test_data.zip", 4, 0) # 139, zip 1.16G GOT-10k
    # implement_get(ctx, "TAPOS/raw/Pre-extracted frames (Google Drive)/flow.tar.gz", 4, 0)
    # implement_upgrade(ctx)
    print(f'*****' * 5)
