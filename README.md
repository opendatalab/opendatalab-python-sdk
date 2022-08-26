# OpenDataLab Python SDK


[![Downloads](https://pepy.tech/badge/opendatalab/month)](https://pepy.tech/project/opendatalab)
[![PyPI](https://img.shields.io/pypi/v/opendatalab)](https://pypi.org/project/opendatalab/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/opendatalab)](https://pypi.org/project/opendatalab/)

---

**IMPORTANT**: OpenDataLab SDK status: WIP, which will not ensure the necessary compatibility of OpenAPI and SDK. As a result, please use the SDK with released version later.  

**Please wait for the released version!!!**

---

OpenDataLab Python SDK is a python library to access [Opendatalab](https://opendatalab.com/)
and use open datasets.  
It provides:

-   A pythonic way to access opendatalab resources.
-   An convient CLI tool `opendatalab` to access open datasets.

## Installation

```console
$ pip3 install opendatalab
```

## Usage:

An **account** is needed to access to opendatalab service.
Please visit [offical websit](https://opendatalab.com/register) to get the account username and password first.

### Help
Show cmd help
```cmd
$ opendatalab -h
$ opendatalab --help

Usage: opendatalab [OPTIONS] COMMAND [ARGS]...

  You can use `opendatalab <command>` to access open datasets.

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
opendatalab, 0.0.1b70
```

### Login
Login with opendatalab username and password. If you haven't an opendatalab account，please register with link: https://opendatalab.com/

```cmd
$ opendatalab login
Username []: wangrui@pjlab.org.cn
Password []: 
Login Successful as wangrui@pjlab.org.cn
or
$ opendatalab login -u aaa@email.com 
Password[]:
```

### Logout
Logout current opendatalab account 
```cmd
$ opendatalab logout
Do you want to logout? [y/N]: y
aaa@email.com Logged Out
```


### List Dataset Files
List dataset files, support prefix of sub_directory
```cmd
# list all dataset files 
$ opendatalab ls  MNIST
total: 4, size: 11.1M
FILE                                                                                                	SIZE
train-labels-idx1-ubyte.gz                                                                          	28.2K
train-images-idx3-ubyte.gz                                                                          	9.5M
t10k-labels-idx1-ubyte.gz                                                                           	4.4K
t10k-images-idx3-ubyte.gz                                                                           	1.6M

# list sub directory files
$ opendatalab ls MNIST/t10k
dataset_name: MNIST, sub_dir: t10k
total: 2, size: 1.6M
FILE                                                                                                	SIZE
t10k-labels-idx1-ubyte.gz                                                                           	4.4K
t10k-images-idx3-ubyte.gz
```

```python
import json
from opendatalab.cli.ls import implement_ls
from opendatalab.cli.utility import ContextInfo
from opendatalab.__version__ import __url__

if __name__ == '__main__':
    """
    ContextInfo: default
        please use shell login first, use: opendatalab login
    """
    ctx = ContextInfo(__url__, "")
    client = ctx.get_client()
    odl_api = client.get_api()

    
    # list demo
    implement_ls(ctx, 'MNIST')
    print(f'*****'*5) 
    
    """运行结果
    total: 4, size: 11.1M
    FILE                                                                                                    SIZE                
    train-labels-idx1-ubyte.gz                                                                              28.2K               
    train-images-idx3-ubyte.gz                                                                              9.5M                
    t10k-labels-idx1-ubyte.gz                                                                               4.4K                
    t10k-images-idx3-ubyte.gz                                                                               1.6M                  
    *************************
    """
```

### Show Dataset Info
```cmd
$ opendatalab info MNIST
========================================
Id                            8
Name                          MNIST
FileBytes                     50.8M
FileCount                     70003
Introduction                  The MNIST database of handwritten digits, available from this page, has a training set of 60,000 ...
PublishDate                   1998
Licenses
Publisher                     National Institute of Standards and Technology
LabelFileTypes                JSON
MediaTypes                    Image
LabelTypes                    Classification
```
```python
from opendatalab.cli.info import _implement_info
from opendatalab.cli.utility import ContextInfo
from opendatalab.__version__ import __url__

if __name__ == '__main__':
    """
    ContextInfo: default
        please use shell login first, use: opendatalab login
    """
    ctx = ContextInfo(__url__, "")
    client = ctx.get_client()
    odl_api = client.get_api()

    
    # get dataset info
    _implement_info(ctx, 'MNIST')
    print(f'*****'*5)
    
    """运行结果
    ========================================
    Id                            8                                                                                                   
    Name                          MNIST                                                                                               
    Filebytes                     50.8M                                                                                               
    Filecount                     70003                                                                                               
    Introduction                  The MNIST database of handwritten digits, available from this page, has a training set of 60,000 ...
    Publishdate                   1998                                                                                                
    Licenses                                                                                                                          
    Publisher                     National Institute of Standards and Technology                                                      
    Labelfiletypes                BIN                                                                                                 
    Mediatypes                    Image                                                                                               
    Labeltypes                    Classification                                                                                       
    *************************
    """
```

### Search Dataset With Keywords
search dataset by keywords
```cmd
$ opendatalab search MNIST
Index     Name                          FileSize  Description                                                                                         	DownloadCount
0         MNIST                         50.8M     The MNIST database of handwritten digits, available from this page, has a training set of 60,000 ...	9
1         Moving_MNIST                  781.9M    The Moving MNIST dataset contains 10,000 video sequences, each consisting of 20 frames. In each v...	0
2         Fashion-MNIST                 52.4M     Fashion-MNIST is a dataset of Zalando's article images—consisting of a training set of 60,000 exa...	1

```
```python
import json
from opendatalab.cli.utility import ContextInfo
from opendatalab.__version__ import __url__

if __name__ == '__main__':
    """
    ContextInfo: default
        please use shell login first, use: opendatalab login
    """
    ctx = ContextInfo(__url__, "")
    client = ctx.get_client()
    odl_api = client.get_api()

    # search demo    
    res_list = odl_api.search_dataset("MNIST")
    for index, res in enumerate(res_list):
        print(f"-->index: {index}, result: {res['name']}")
    print(f'*****'*5)   
    
    """运行结果
    -->index: 0, result: MNIST
    -->index: 1, result: Moving_MNIST
    -->index: 2, result: Fashion-MNIST
    *************************
    """
```

### Download Dataset Files Into Local
Please change your local path, then run below command.
```cmd
$ opendatalab get MNIST/t10k

local dir: ~/MNIST
Scan done, total files: 2, total size: 1.65M
Start downloading file: ~/t10k-images-idx3-ubyte.gz ...
Start downloading file: ~/MNIST/t10k-labels-idx1-ubyte.gz ...
100%|██

```
```python
import json
from opendatalab.cli.get import _implement_get
from opendatalab.cli.utility import ContextInfo
from opendatalab.__version__ import __url__
if __name__ == '__main__':
    ctx = ContextInfo(__url__, "")
    client = ctx.get_client()
    odl_api = client.get_api()

    # download files demo
    # Reminder: run this snippet at local path which you want to save.
    _implement_get(ctx, 'MNIST', 4 , 0, True)
    print(f'*****'*5)
    '''运行结果
    local dir: /Users/wangrui/work/codes/opendatalab/opendatalab-python-sdk/MNIST
    Scan done, total files: 4, total size: 11.6M
    0%|                                                                                                  | 0.00/11.6M [00:00<?, ?B/s]
    Start downloading file: /Users/wangrui/work/codes/opendatalab/opendatalab-python-sdk/MNIST/t10k-images-idx3-ubyte.gz ...
    Start downloading file: /Users/wangrui/work/codes/opendatalab/opendatalab-python-sdk/MNIST/t10k-labels-idx1-ubyte.gz ...
    Start downloading file: /Users/wangrui/work/codes/opendatalab/opendatalab-python-sdk/MNIST/train-images-idx3-ubyte.gz ...
    Start downloading file: /Users/wangrui/work/codes/opendatalab/opendatalab-python-sdk/MNIST/train-labels-idx1-ubyte.gz ...
    100%|█████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 11.6M/11.6M [00:04<00:00, 2.65MB/s]
    '''
```

## Python Develop Sample
```python
import json
from opendatalab.cli.ls import _implement_ls
from opendatalab.cli.get import _implement_get
from opendatalab.cli.info import _implement_info
from opendatalab.cli.utility import ContextInfo
from opendatalab.__version__ import __url__

if __name__ == '__main__':
    """
    ContextInfo: default
        please use shell login first, use: opendatalab login
    """
    ctx = ContextInfo(__url__, "")
    client = ctx.get_client()
    odl_api = client.get_api()

    # 1.search demo    
    res_list = odl_api.search_dataset("MNIST")
    for index, res in enumerate(res_list):
        print(f"-->index: {index}, result: {res['name']}")
    print(f'*****'*5)   
    
    # 2.list demo
    _implement_ls(ctx, 'MNIST')
    print(f'*****'*5)   
    
    # 3.get dataset info
    _implement_info(ctx, 'MNIST')
    print(f'*****'*5)
    
    # 4.read file demo 
    dataset = client.get_dataset('MNIST') 
    with dataset.get('data_info/info.json', compressed=False) as fd:
        content = json.load(fd)
        print(f"{content}")    
    print(f'*****'*5)

    # 5.download files demo
    #参数：context, 数据集名称， 线程数，下载限速，是否为下载文件
    _implement_get(ctx, 'MNIST', 4 , 0, True)
    print(f'*****'*5)
    
```

## Documentation
More information can be found on the [documentation site](https://opendatalab.com/docs)