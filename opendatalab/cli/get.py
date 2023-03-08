#!/usr/bin/env python3
#
# Copyright 2022 Shanghai AI Lab. Licensed under MIT License.
#
import logging
import os
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List

import click
import parfive
import requests
from tqdm import tqdm

from opendatalab.cli.policy import private_policy_url, service_agreement_url
from opendatalab.cli.utility import ContextInfo, exception_handler
from opendatalab.exception import OdlDataNotExistsError


def handler(dwCtrlType):
    if dwCtrlType == 0:  # CTRL_C_EVENT
        pid = os.getpid()
        os.kill(pid, 9)


if sys.platform == "win32":
    import win32api
    win32api.SetConsoleCtrlHandler(handler, True)

@exception_handler
def download_from_url(url:str, pth: str, file_name:str):
    """This function perform a resumable download for a single object

    Args:
        url (str): single download url
        pth(str): local download path
        file_name (str): file name(may contain relative path)
    """
    response = requests.get(url, stream = True)
    
    # get total file size
    file_size = int(response.headers['content-length'])
    
    target = os.path.join(pth, file_name)
    # indicate a file-downloaing not complete
    if os.path.exists(target):
        first_byte = os.path.getsize(target)
    else:
        # indicate a new file
        first_byte = 0
    
    # check actual size and server size
    if first_byte >= file_size:
        click.secho('Download Complete')
        sys.exit(1)
    
    header = {"Range": f"bytes = {first_byte}-{file_size}"}
    
    pbar = tqdm(total=file_size,
                initial= first_byte,
                unit = 'B',
                unit_scale= True,
                desc = 'Downloading Progress:')
    
    req = requests.get(url, headers= header, stream=True)
    
    with(open(target, 'ab')) as f:
        for chunk in req.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
                pbar.update(1024)
    pbar.close()
    return file_size
    
    
@exception_handler
def implement_get(obj: ContextInfo, name: str, conn = 5):
    """
    implementation for getting dataset files
    Args:
        obj (ContextInfo):
        name (str):
        thread (int):
        compressed (bool):
    Returns:
    """
    ds_split = name.split("/")
    if len(ds_split) > 1:
        dataset_name = ds_split[0]
        sub_dir = "/".join(ds_split[1:])
    else:
        dataset_name = name
        sub_dir = ""
    
    # print(name, ds_split ,dataset_name)
    
    client = obj.get_client()
    data_info = client.get_api().get_info(dataset_name)
    info_dataset_name = data_info['name']
    info_dataset_id = data_info['id']
    
    dataset_res_dict = client.get_api().get_dataset_files(dataset_name=info_dataset_name,
                                                          prefix = sub_dir)
    # print(dataset_res_dict)
    
    # obj list constuct
    obj_info_list = []
    for info in dataset_res_dict['list']:
        curr_dict = {}
        if not info['isDir']:
            curr_dict['size'] = info['size']
            curr_dict['name'] = info['path']
            obj_info_list.append(curr_dict)

    # if not sub_dir:
    print(obj_info_list, sub_dir)
    download_urls_list = client.get_api().get_dataset_download_urls(
                                                            dataset_id=info_dataset_id, 
                                                            dataset_list=obj_info_list)
    # print(obj_info_list)
    print('____________________________________________________-')
    
    
    url_list = []
    item_list = []
    for item in download_urls_list:
        url_list.append(item['url'])
        item_list.append(item['name'])
    
    print(url_list[0], item_list[0])

    
    
    local_dir = Path.cwd().joinpath(info_dataset_name)
    
    download_data = client.get_api().get_download_record(info_dataset_name)
    has_download = download_data['hasDownload']

    if not has_download:
        if click.confirm(f"<<User Service Agreement>>: {service_agreement_url}"
                         f"\n<<Privacy Policy>>: {private_policy_url}"
                         f"\n[Warning]: Before downloading, please agree above content."):
            client.get_api().submit_download_record(info_dataset_name, download_data)
        else:
            click.secho('bye~')
            sys.exit(1)
    
    if click.confirm(f"Download files into local directory: {local_dir} ?", default=True):
        if not Path(local_dir).exists():
            Path(local_dir).mkdir(parents=True)
            print(f"create local dir: {local_dir}")
    else:
        click.secho('bye~')
        sys.exit(1)
        
        
    ########################################################################
    size = download_from_url(url_list[0], pth=local_dir, file_name = item_list[0])
    ########################################################################
    print(size)
    
    
    # downloader = parfive.Downloader(max_conn = conn,
    #                                 max_splits= 5,
    #                                 progress= True)
    
    # for idx, url in enumerate(url_list):
    #         downloader.enqueue_file(url, path = local_dir, filename=item_list[idx])
        
    # results = downloader.download()
    
    # for i in results:
    #     click.echo(i)
    
    # err_str = ''
    # for err in results.errors:
    #     err_str += f"{err.url} \t {err.exception}\n"
    # if not err_str:
    #     print(f"{info_dataset_name}, download completed!")
    # else:
    #     sys.exit(err_str)