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
def implement_get(obj: ContextInfo, name: str, conn = 5):
    """
    implementation for getting dataset files
    Args:
        obj (ContextInfo):
        name (str):
        thread (int):
        limit_speed (int):
        compressed (bool):
    Returns:
    """
    ds_split = name.split("/")
    if len(ds_split) > 1:
        dataset_name = ds_split[0]
    else:
        dataset_name = name
    
    client = obj.get_client()
    data_info = client.get_api().get_info(dataset_name)
    info_dataset_name = data_info['name']
    info_dataset_id = data_info['id']
    
    dataset_res_dict = client.get_api().get_dataset_files(dataset_name=info_dataset_name)
    # obj list constuct
    obj_info_list = []
    for info in dataset_res_dict['list']:
        curr_dict = {}
        if not info['isDir']:
            curr_dict['size'] = info['size']
            curr_dict['name'] = info['path']
            obj_info_list.append(curr_dict)
    download_urls_list = client.get_api().get_dataset_download_urls(
                                                            dataset_id=info_dataset_id, 
                                                            dataset_list=obj_info_list)
    url_list = []
    item_list = []
    for item in download_urls_list:
        url_list.append(item['url'])
        item_list.append(item['name'])
    
    
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
        
    downloader = parfive.Downloader(max_conn = conn,
                                    max_splits= 5,
                                    progress= True)
    
    for idx, url in enumerate(url_list):
            downloader.enqueue_file(url, path = local_dir, filename=item_list[idx])
        
    results = downloader.download()
    
    for i in results:
        click.echo(i)
    
    err_str = ''
    for err in results.errors:
        err_str += f"{err.url} \t {err.exception}\n"
    if not err_str:
        print(f"{info_dataset_name}, download completed!")
    else:
        sys.exit(err_str)