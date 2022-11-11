# OpenDataLab Python SDK


[![Downloads](https://pepy.tech/badge/opendatalab/month)](https://pepy.tech/project/opendatalab)
[![PyPI](https://img.shields.io/pypi/v/opendatalab)](https://pypi.org/project/opendatalab/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/opendatalab)](https://pypi.org/project/opendatalab/)

---

**IMPORTANT**: OpenDataLab SDK WIP, not ensure the necessary compatibility of OpenAPI and SDK. As a result, please use the SDK with the **latest** version.  

---

OpenDataLab Python SDK is a python library to access [Opendatalab](https://opendatalab.org.cn/)
and use open datasets.  
It provides:

-   A pythonic way to access opendatalab resources.
-   A convenient CLI tool `odl` to access open datasets.

## Installation

```console
$ pip3 install opendatalab
```

## Usage:

An **account** is needed to access to opendatalab platform.
Please visit [offical websit](https://opendatalab.org.cn/register) to get the account username and password first.

### Help
Show cmd help
```cmd
$ odl -h
$ odl --help

Usage: odl [OPTIONS] COMMAND [ARGS]...

  You can use `odl <command>` to access open datasets.

Options:
  --version   Show the version and exit.
  -h, --help  Show this message and exit.

Commands:
  get      Get(Download) dataset files into local path.
  info     Print dataset info.
  login    Login opendatalab with account.
  logout   Logout opendatalab account.
  ls       List files of the dataset.
  search   Search dataset info.
  version  Show opendatalab version.
```

### Version
```cmd
$ odl version
odl version, current: 0.0.2, svc: 1.8
```

### Login
Login with opendatalab username and password. If you haven't an opendatalab account，please register with link: https://opendatalab.org.cn/

```cmd
$ odl login
Username []: someone@example.com
Password []: 
Login successfully as someone@example.com
or
$ odl login -u someone@example.com
Password[]:
```

### Logout
Logout current opendatalab account 
```cmd
$ odl logout
Do you want to logout? [y/N]: y
someone@example.com logout
```


### List Dataset Files
List dataset files, support prefix of sub_directory
```cmd
# list all dataset files 
$ odl ls  MNIST
total: 4, size: 11.1M
+----------------------------+--------------+
| File Name                  | Size         |
+----------------------------+--------------+
| train-labels-idx1-ubyte.gz | 28.2K        |
+----------------------------+--------------+
| train-images-idx3-ubyte.gz | 9.5M         |
+----------------------------+--------------+
| t10k-labels-idx1-ubyte.gz  | 4.4K         |
+----------------------------+--------------+
| t10k-images-idx3-ubyte.gz  | 1.6M         |
+----------------------------+--------------+                                                                          	1.6M

# list sub directory files
$ odl ls MNIST/t10k
total: 2, size: 1.6M
+---------------------------+--------------+
| File Name                 | Size         |
+---------------------------+--------------+
| t10k-labels-idx1-ubyte.gz | 4.4K         |
+---------------------------+--------------+
| t10k-images-idx3-ubyte.gz | 1.6M         |
+---------------------------+--------------+
```

```cmd
# download dataset files into local  
# get all files of dataset  
$ odl get MNIST  

# get partial files of dataset  
$ odl get MNIST/t10k  
```

## Python Develop Sample
```python
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
    for index, res in enumerate(res_list):
        print(f"index: {index}, result: {res['name']}")

    # implement_search("coco")
    print(f'*****'*8)

    # 2. list demo
    implement_ls(ctx, 'TAO')
    print(f'*****' * 8)

    # 3. read file online demo
    dataset = client.get_dataset('FB15k')
    with dataset.get('meta/info.json', False) as fd:
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
```

## Documentation
More information can be found on the [documentation site](https://opendatalab.org.cn/docs)