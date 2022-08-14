#!/usr/bin/env python3
#
# Copyright 2022 Shanghai AI Lab. Licensed under MIT License.
#
import os
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List

import click
import oss2
from tqdm import tqdm

from opendatalab.cli.utility import ContextInfo, exception_handler

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
def _implement_get(obj: ContextInfo, name: str, thread: int, limit_speed: int, compressed: bool = True) -> None:
    ds_split = name.split("/")
    if len(ds_split) > 1:
        dataset_name = ds_split[0]
        sub_dir = "/".join(ds_split[1:])
    else:
        dataset_name = name
        sub_dir = ""

    local_dir = Path.cwd().joinpath(dataset_name)
    if not Path(local_dir).exists():
        Path(local_dir).mkdir(parents=True)

    print(f"local dir: {local_dir}")

    # refactor below codes for retry downloading objects
    client = obj.get_client()
    dataset = client.get_dataset(dataset_name)
    prefix = dataset.get_object_key_prefix(compressed)
    bucket = dataset.get_oss_bucket()

    total_files, total_size = 0, 0
    object_info_list = []
    download_info_body = []

    for info in oss2.ObjectIteratorV2(bucket, prefix):
        if not info.is_prefix() and not info.key.endswith("/"):
            file_name = "/".join(info.key.split("/")[2:])
            f_name = Path(file_name).name
            if not sub_dir:
                object_info_list.append(info)
                total_files = total_files + 1
                total_size = total_size + info.size
                download_info_body.append({"name": f_name, "size": info.size})
            elif sub_dir and file_name.startswith(sub_dir):
                object_info_list.append(info)
                total_files = total_files + 1
                total_size = total_size + info.size
                download_info_body.append({"name": f_name, "size": info.size})
            else:
                pass

    client.get_api().call_download_log(dataset_name, download_info_body)
    click.echo(f"Scan done, total files: {len(object_info_list)}, total size: {tqdm.format_sizeof(total_size)}")
    limit_speed_per_thread = get_oss_traffic_limit(int(limit_speed * 1024 * 8 / thread))

    while True:
        error_object_list = download_objects_retry(bucket=bucket,
                                                   local_dir=local_dir,
                                                   object_info_list=object_info_list,
                                                   total_size=total_size,
                                                   limit_speed_per_thread=limit_speed_per_thread,
                                                   thread=thread)
        if len(error_object_list) > 0:
            bucket = dataset.refresh_oss_bucket()
            download_objects_retry(bucket=bucket,
                                   local_dir=local_dir,
                                   object_info_list=error_object_list,
                                   total_size=None,
                                   limit_speed_per_thread=limit_speed_per_thread,
                                   thread=thread)
        else:
            break

    print("Download Completed!")


def download_objects_retry(bucket, local_dir, object_info_list, total_size, limit_speed_per_thread, thread) -> List:
    pbar = tqdm(total=total_size, unit="B", unit_scale=True)
    lock = threading.RLock()
    error_object_list = []

    # real download procedure
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
        return error_object_list

    return error_object_list
