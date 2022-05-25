# Future API

## Config File

 ~/.opendatalab/config.json

## CLI

### General Options

```
-h --help
--version
-v --verbose
-c --config
-H --host

```

### Help

```bash
$ opendatalab help

...
```

### Show Version

```bash
$ opendatalab version
0.0.1
```

### Logout

```bash
$ opendatalab logout
bob@abc.com Logged Out
```

### Login

```bash
$ opendatalab login
  -h --help       Show help info
  -u --username   User name, will prompt if absent.
  -p --password   User password, will prompt if absent.
```

e.g.
```bash
$ opendatalab login -u bob@abc.com -p somePassword
Login Successful as bob@abc.com
```

e.g.
```bash
$ opendatalab login
Login with your opendatalab account. If you don't have an account, go to https://opendatalab.com to create one.
Username: bob@abc.com
Password:                  <- do not show password during typing
Login Successful as bob@abc.com
```

e.g.
```bash
$ opendatalab login --username bob@abc.com
Password:                  <- do not show password during typing
Login Successful as bob@abc.com
```

e.g.
```bash
$ opendatalab login -p somePassword
Login with your opendatalab account. If you don't have an account, go to https://opendatalab.com to create one.
Username: bob@abc.com
Login Successful as bob@abc.com
```

### Search

```bash
$ opendatalab search coco
NAME           DESCRIPTION                                                                DOWNLOADS
COCO_2014      COCO is a large-scale object detection, segmentation, and captioning ...   22
COCO_2017      COCO is a large-scale object detection, segmentation, and captioning ...   33
```

### Info

```bash
$ opendatalab info COCO_2014
Name: COCO_2014
Display Name: COCO 2014
Description: xxxx
... other fields
```

### list (alias: ls)

```bash
$ opendatalab ls COCO_2014
FILE                                       SIZE
annotations_trainval2014.zip               252.9MB
image_info_test2014.zip                    763.5KB
test2014.zip                               6.7GB
train2014.zip                              13.5GB
val2014.zip                                6.6GB
```

### download (alias: dl)

TODO



