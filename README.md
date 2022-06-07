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

-   A pythonic way to access opendatalab resources by OpenDataHub OpenAPI.
-   An convient CLI tool `opendatalab` to access open datasets.
-   Rich information about the open datasets.

## Installation

```console
pip3 install opendatalab
```

## Usage:

An **account** is needed to access to opendatalab service.
Please visit [offical websit](https://opendatalab.com/register) to get the account username and password first.

### Help
show cmd help
```cmd
opendatalab -h
opendatalab --help
```

### Show Version
```cmd
opendatalab version
# opendatalab, 0.0.1b1
```

### Login
login with opendatalab username and password 
```cmd
$ opendatalab login 
Username: aaa@email.com 
Password:
# Login as aaa@email.com

$ opendatalab login -u aaa@email.com 
Password:
# Login as aaa@email.com

```
or 
```python
from opendatalab import Client
odl = Client.auth(username, pasword)

```

### Logout
logout current opendatalab account 
```cmd
opendatalab logout
```
or 
```python
from opendatalab import opendatalab
Client.logout()
```

### ls 
list all dataset by offset, limit
```cmd
opendatalab ls -n coco
```
or
```python
from opendatalab import opendatalab
opendatalab.ls(name='coco')
```

### info
show dataset info in json format
```cmd
opendatalab info coco
```
or
```python
from opendatalab import opendatalab
opendatalab.get_info()
```

### search
search dataset by name
```cmd
opendatalab search coco 
```
or
```python
from opendatalab import opendatalab
opendatalab.search('coco')
```

### get
get dataset files into local path
```cmd
opendatalab get coco 
```
or
```python
from opendatalab import opendatalab
opendatalab.get(name='coco')
``` 

## Documentation

More information can be found on the [documentation site](https://opendatalab.com/docs)