#!/usr/bin/env python3
#
# Copyright 2022 Shanghai AI Lab. Licensed under MIT License.
#
import os
import sys
from pathlib import Path
from typing import List

import click
from tqdm import tqdm

from opendatalab.cli.policy import private_policy_url, service_agreement_url
from opendatalab.cli.utility import ContextInfo, exception_handler
from opendatalab.client import downloader
from opendatalab.exception import OdlDataNotExistsError


def handler(dwCtrlType):
    if dwCtrlType == 0:  # CTRL_C_EVENT
        pid = os.getpid()
        os.kill(pid, 9)


if sys.platform == "win32":
    import win32api
    win32api.SetConsoleCtrlHandler(handler, True)
    
    
@exception_handler
def implement_get(obj: ContextInfo, name: str, destination:str, num_workers:int):
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
    
    # print(name, ds_split ,dataset_name, sub_dir)
    
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
            curr_dict['name'] = os.path.join(sub_dir,info['path'])
            obj_info_list.append(curr_dict)

    # if not sub_dir:
    # print(obj_info_list, sub_dir)
    download_urls_list = client.get_api().get_dataset_download_urls(
                                                            dataset_id=info_dataset_id, 
                                                            dataset_list=obj_info_list)
    # print(obj_info_list)
    print('___________________________________________________')
    
    
    url_list = []
    item_list = []
    for item in download_urls_list:
        url_list.append(item['url'])
        item_list.append(item['name'])
    
    # print(url_list[0], item_list[0])

    local_dir = destination
    
    download_data = client.get_api().get_download_record(info_dataset_name)
    has_download = download_data['hasDownload']

    if not has_download:
        if click.confirm(f"<<User Service Agreement>>: {service_agreement_url}"
                         f"\n<<Privacy Policy>>: {private_policy_url}"
                         f"\n[Warning]: Before downloading, please agree above content."):
            client.get_api().submit_download_record(info_dataset_name, download_data)
        else:
            click.secho('See you next time~!')
            sys.exit(1)
    
    if click.confirm(f"Download files into local directory: {local_dir} ?", default=True):
        if not Path(local_dir).exists():
            Path(local_dir).mkdir(parents=True)
            print(f"create local dir: {local_dir}")
    else:
        click.secho('See you next time~!')
        sys.exit(1)
        
    # print(url_list[0], item_list[0])
    ########################################################################

    with tqdm(total = len(url_list)) as pbar:
        for idx in range(len(url_list)):
            if len(item_list[idx].split('/')) == 1:
                filename = item_list[idx]
                prefix = ''
            else:
                filename = item_list[idx].split('/')[-1]
                prefix = os.path.dirname(item_list[idx])

            click.echo(f"Downloading No.{idx+1} of total {len(url_list)} files\n")
            if os.path.exists(os.path.join(destination,info_dataset_name, prefix,filename)):
                click.echo('target already exists, jumping to next!')
                continue
            downloader.Downloader(url = url_list[idx], 
                                  filename=item_list[idx], 
                                  download_dir = os.path.join(destination, info_dataset_name), 
                                  blocks_num= num_workers).start()
            pbar.update(1)
    click.echo(f"\nDownload Complete!")
