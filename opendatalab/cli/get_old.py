#!/usr/bin/env python3
#
# Copyright 2022 Shanghai AI Lab. Licensed under MIT License.
#
import logging
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List

import click
import oss2
from tqdm import tqdm

oss2.set_stream_logger(level=logging.CRITICAL)

from opendatalab.cli.policy import service_agreement_url, private_policy_url
from opendatalab.cli.utility import ContextInfo, exception_handler
from opendatalab.exception import OdlDataNotExistsError

key_to_get_size_map = {}


def get_oss_traffic_limit(limit_speed):
    if limit_speed <= 0:
        return 0
    if limit_speed < 245760:
        return 245760
    if limit_speed > 838860800:
        return 838860800
    return limit_speed


def download_object(
        bucket: oss2.Bucket,
        obj_key: str,
        lock: threading.RLock,
        root: str,
        pbar: tqdm,
        limit_speed: int,
):
    def progress_callback(bytes_consumed, _):
        with lock:
            global key_to_get_size_map
            if obj_key not in key_to_get_size_map:
                key_to_get_size_map[obj_key] = 0
            pbar.update(bytes_consumed - key_to_get_size_map[obj_key])
            key_to_get_size_map[obj_key] = bytes_consumed
            print(f"********"*5)
            for k, v in key_to_get_size_map.items():
                print(f"\t{k} {v} bytes_consumed: {bytes_consumed}")
            print(f"********"*5)


    try:
        headers = dict()
        # headers['ETag'] = obj_info.etag
        if limit_speed > 0:
            headers[oss2.models.OSS_TRAFFIC_LIMIT] = str(limit_speed)

        filename = os.path.join(root, obj_key.split("/")[-1])
        # print(f"Start downloading file: {filename} ...")

        oss2.resumable_download(
            bucket,
            obj_key,
            filename,
            multiget_threshold=5 * 1024 * 1024 * 1024,  # 50M -> 500G
            part_size=10 * 1024 * 1024,  # 10M
            progress_callback=progress_callback,
            num_threads=4,
            headers=headers,
        )
        return True, None
    except oss2.exceptions.InconsistentError as e:
        click.secho(f"Resumable download occurs InconsistentError", fg='red')
        return False, e
    except oss2.exceptions.ServerError as e:
        click.secho(f"Resumable download occurs ServerError", fg='red')
        return False, e
    except Exception as e:
        click.secho(f"Resumable download occurs Exception", fg='red')
        return False, e


@exception_handler
def implement_get(obj: ContextInfo, name: str, thread: int, limit_speed: int, compressed: bool = True) -> None:
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
        sub_dir = "/".join(ds_split[1:])
    else:
        dataset_name = name
        sub_dir = ""

    client = obj.get_client()
    dataset = client.get_dataset(dataset_name)
    prefix = dataset.get_object_key_prefix(compressed)
    bucket = dataset.get_oss_bucket()

    total_files, total_size = 0, 0
    obj_info_list = []
    download_info_body = []

    for info in oss2.ObjectIteratorV2(bucket, prefix):
        if not info.is_prefix() and not info.key.endswith("/"):
            file_name = "/".join(info.key.split("/")[2:])
            f_name = Path(file_name).name
            if not sub_dir:
                obj_info_list.append(info.key)
                total_files = total_files + 1
                total_size = total_size + info.size
                download_info_body.append({"name": f_name, "size": info.size})
            elif sub_dir and file_name.startswith(sub_dir):
                obj_info_list.append(info.key)
                total_files = total_files + 1
                total_size = total_size + info.size
                download_info_body.append({"name": f_name, "size": info.size})
            else:
                pass

    if len(download_info_body) == 0:
        raise OdlDataNotExistsError(error_msg=f"{name} not exists!")

    client.get_api().call_download_log(dataset_name, download_info_body)
    click.echo(f"Scan done, total files: {len(obj_info_list)}, total size: {tqdm.format_sizeof(total_size)}")

    has_download = client.get_api().get_download_record(dataset_name)

    if not has_download:
        if click.confirm(f"[Warning]: Before downloading, please agree below content."
                         f"\nUser Service Agreement, link: {service_agreement_url}"
                         f"\nPrivacy Policy, link: {private_policy_url}"):
            client.get_api().submit_download_record(dataset_name)
            click.echo("\n")

    limit_speed_per_thread = get_oss_traffic_limit(int(limit_speed * 1024 * 8 / thread))
    local_dir = Path.cwd().joinpath(dataset_name)
    if click.confirm(f"Do you want to download files into local directory: {local_dir} ?", default=True):
        if not Path(local_dir).exists():
            Path(local_dir).mkdir(parents=True)
            print(f"create local dir: {local_dir}")

    error_object_list = get_objects_retry(bucket=bucket,
                                          local_dir=local_dir,
                                          obj_info_list=obj_info_list,
                                          total_size=total_size,
                                          limit_speed_per_thread=limit_speed_per_thread,
                                          thread=thread)

    index = 1
    while len(error_object_list) > 0:
        global key_to_get_size_map
        bucket = dataset.refresh_oss_bucket()
        total_size_remain = total_size  # - sum(key_to_get_size_map.values())
        error_object_list = get_objects_retry(bucket=bucket,
                                              local_dir=local_dir,
                                              obj_info_list=error_object_list,
                                              total_size=total_size_remain,
                                              limit_speed_per_thread=limit_speed_per_thread,
                                              thread=thread)
        print(f"retry times: {index}")
        index = index + 1
        time.sleep(1)

        if len(error_object_list) > 0:
            continue
        else:
            break

    if index == 8:
        print(f"{dataset_name} ,download failure!")
    else:
        print(f"{dataset_name} ,download completed!")


def get_objects_retry(bucket, local_dir, obj_info_list, total_size, limit_speed_per_thread, thread) -> List:
    pbar = tqdm(total=total_size, unit="B", unit_scale=True)
    click.secho(f"current timestamp: {int(round(time.time()) * 1000)}", fg='green')
    lock = threading.RLock()
    error_object_list = []

    # real download procedure
    with ThreadPoolExecutor(max_workers=thread) as executor:
        future_to_obj = {
            executor.submit(
                download_object, bucket, obj, lock, local_dir, pbar, limit_speed_per_thread
            ): obj
            for obj in obj_info_list
        }
        for future in as_completed(future_to_obj):
            obj = future_to_obj[future]
            success, _ = future.result()
            if not success:
                error_object_list.append(obj)

    pbar.close()
    # error_object_list = list(dict.fromkeys(error_object_list))
    print(f"reprocessed obj num: {len(error_object_list)}")

    return error_object_list
