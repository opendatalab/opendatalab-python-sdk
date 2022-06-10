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

### Show Version
```cmd
$ opendatalab version
opendatalab, 0.0.1b68
```

### Login
login with opendatalab username and password 
```cmd
$ opendatalab login 
$ Username: aaa@email.com 
$ Password:

Login as aaa@email.com

$ opendatalab login -u aaa@email.com 
$ Password:

Login as aaa@email.com

```


### Logout
logout current opendatalab account 
```cmd
$ opendatalab logout
Do you want to logout? [y/N]: y
aaa@email.com Logged Out
```


### ls 
list dataset files, support prefix of sub_directory
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

### info
show dataset info
```cmd
$ opendatalab info MNIST
========================================
Id                            8
Name                          MNIST
Filebytes                     50.8M
Filecount                     70003
Introduction                  The MNIST database of handwritten digits, available from this page, has a training set of 60,000 ...
Publishdate                   1998
Licenses
Publisher                     National Institute of Standards and Technology
Labelfiletypes                JSON
Mediatypes                    Image
Labeltypes                    Classification
```

### search
search dataset by keywords
```cmd
$ opendatalab search MNIST
Index     Name                          FileSize  Description                                                                                         	DownloadCount
0         MNIST                         50.8M     The MNIST database of handwritten digits, available from this page, has a training set of 60,000 ...	9
1         Moving_MNIST                  781.9M    The Moving MNIST dataset contains 10,000 video sequences, each consisting of 20 frames. In each v...	0
2         Fashion-MNIST                 52.4M     Fashion-MNIST is a dataset of Zalando's article images—consisting of a training set of 60,000 exa...	1

```

### get
get dataset files into local path
```cmd
$ opendatalab get MNIST/t10k
local dir: ~/MNIST
Scan done, total files: 2, total size: 1.65M
Start downloading file: ~/t10k-images-idx3-ubyte.gz ...
Start downloading file: ~/MNIST/t10k-labels-idx1-ubyte.gz ...
100%|██

```


## Documentation

More information can be found on the [documentation site](https://opendatalab.com/docs)