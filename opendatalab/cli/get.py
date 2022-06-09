#!/usr/bin/env python3
#
# Copyright 2022 Shanghai AI Lab. Licensed under MIT License.
#
from pathlib import Path
import threading
import click
import oss2
import os

from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed, thread
from opendatalab.cli.utility import ContextInfo, exception_handler
from opendatalab.client.client import Client


key_to_downloaded_size_map = {}

def download_object(
    bucket: oss2.Bucket,
    object_info: oss2.models.SimplifiedObjectInfo,
    lock: threading.RLock,
    root: str,
    pbar: tqdm,
    limit_speed: int,
):
    def progress_callback(bytes_consumed, _):
        with lock:
            global key_to_downloaded_size_map
            if object_info.key not in key_to_downloaded_size_map:
                key_to_downloaded_size_map[object_info.key] = 0
            pbar.update(bytes_consumed - key_to_downloaded_size_map[object_info.key])
            key_to_downloaded_size_map[object_info.key] = bytes_consumed

    try:
        headers = dict()
        if limit_speed > 0:
            headers[oss2.models.OSS_TRAFFIC_LIMIT] = str(limit_speed)
            
        filename = os.path.join(root, object_info.key.split("/")[-1])
        print(f"Start downloading file: {filename} ...")
        oss2.resumable_download(
            bucket,
            object_info.key,
            filename,
            multiget_threshold=50 * 1024 * 1024,
            part_size=10 * 1024 * 1024,
            progress_callback=progress_callback,
            num_threads=1,
            headers=headers,
        )
        return True, None
    except Exception as e:
        return False, e


def get_oss_traffic_limit(limit_speed):
    if limit_speed <= 0:
        return 0
    if limit_speed < 245760:
        return 245760
    if limit_speed > 838860800:
        return 838860800
    return limit_speed

@exception_handler
def _implement_get(obj: ContextInfo, name: str, thread: int , limit_speed: int) -> None:
    client = obj.get_client()
    dataset = client.get_dataset(name)
    bucket = dataset.get_oss_bucket()
    prefix = dataset.get_object_key_prefix()
    object_info_list = []
    download_info_body = []
    local_dir = Path.cwd().joinpath(name)
    if not Path(local_dir).exists():
        Path(local_dir).mkdir(parents=True)
        
    total_size = 0
    print(f"local dir: {local_dir}")
    for info in oss2.ObjectIteratorV2(bucket, prefix):
        object_info_list.append(info)
        total_size += info.size
        file_name = Path(info.key).name
        download_info_body.append({"name": file_name, "size": info.size})
        
    client.get_api().call_download_log(name, download_info_body)
    click.echo(f"Scan done, total size: {tqdm.format_sizeof(total_size)}, files: {len(object_info_list)}")

    pbar = tqdm(total=total_size, unit="B", unit_scale=True)
    lock = threading.RLock()
    error_object_list = []
    
    limit_speed_per_thread = get_oss_traffic_limit(int(limit_speed * 1024 * 8 / thread))
    with ThreadPoolExecutor(max_workers=thread) as executor:
        future_to_obj = {
            executor.submit(
                download_object, bucket, obj, lock, local_dir, pbar, limit_speed_per_thread
            ): obj
            for obj in object_info_list
        }
        for future in as_completed(future_to_obj):
            obj = future_to_obj[future]
            success, _ = future.result()
            if not success:
                error_object_list.append(obj)

    pbar.close()
    if len(error_object_list) != 0:
        pass
        # TODO

