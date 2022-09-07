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
import oss2
from tqdm import tqdm

from opendatalab.cli.policy import service_agreement_url, private_policy_url
from opendatalab.cli.utility import ContextInfo, exception_handler
from opendatalab.exception import OdlDataNotExistsError

oss2.set_stream_logger(level=logging.CRITICAL)
key_to_get_size_map = {}


def handler(dwCtrlType):
    if dwCtrlType == 0:  # CTRL_C_EVENT
        pid = os.getpid()
        os.kill(pid, 9)


if sys.platform == "win32":
    import win32api
    win32api.SetConsoleCtrlHandler(handler, True)


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

            # sys.stdout.flush()
            pbar.update(bytes_consumed - key_to_get_size_map[obj_key])
            key_to_get_size_map[obj_key] = bytes_consumed

    try:
        headers = dict()
        if limit_speed > 0:
            headers[oss2.models.OSS_TRAFFIC_LIMIT] = str(limit_speed)

        filename = os.path.join(root, obj_key.split("/")[-1])

        oss2.resumable_download(
            bucket,
            obj_key,
            filename,
            multiget_threshold=50 * 1024 * 1024,  # 50M -> 500G(cdn)
            part_size=10 * 1024 * 1024,  # 10M
            progress_callback=progress_callback,
            num_threads=1,
            headers=headers,
        )
        return True, None
    except oss2.exceptions.InconsistentError as e:
        return False, e
    except oss2.exceptions.ServerError as e:
        return False, e
    except Exception as e:
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
    info_data_name = client.get_api().get_info(dataset_name)['name']
    dataset = client.get_dataset(info_data_name)
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
    click.echo(f"Scan done, total files: {len(obj_info_list)}, total size: {tqdm.format_sizeof(total_size,divisor=1024)}")

    download_data = client.get_api().get_download_record(dataset_name)
    has_download = download_data['hasDownload']

    if not has_download:
        if click.confirm(f"<<User Service Agreement>>: {service_agreement_url}"
                         f"\n<<Privacy Policy>>: {private_policy_url}"
                         f"\n[Warning]: Before downloading, please agree above content."):
            client.get_api().submit_download_record(dataset_name, download_data)
        else:
            click.secho('bye~')
            sys.exit(1)

    limit_speed_per_thread = get_oss_traffic_limit(int(limit_speed * 1024 * 8 / thread))

    local_dir = Path.cwd().joinpath(dataset_name)
    if click.confirm(f"Download files into local directory: {local_dir} ?", default=True):
        if not Path(local_dir).exists():
            Path(local_dir).mkdir(parents=True)
            print(f"create local dir: {local_dir}")
    else:
        click.secho('bye~')
        sys.exit(1)

    pbar = tqdm(total=total_size, unit="B", unit_divisor=1024, unit_scale=True, position=0)

    index = 0
    is_running = True
    while is_running:
        global key_to_get_size_map
        bucket = dataset.refresh_oss_bucket()
        error_object_list = get_objects_retry(bucket=bucket,
                                              local_dir=local_dir,
                                              obj_info_list=obj_info_list,
                                              pbar=pbar,
                                              limit_speed_per_thread=limit_speed_per_thread,
                                              thread=thread)
        index = index + 1
        time.sleep(1)
        if len(error_object_list) > 0:
            obj_info_list = error_object_list
            is_running = True
            continue
        else:
            is_running = False
            break

    pbar.close()
    print(f"{dataset_name} ,download completed!")


def get_objects_retry(bucket, local_dir, obj_info_list, pbar, limit_speed_per_thread, thread) -> List:
    lock = threading.RLock()
    error_object_list = []
    with ThreadPoolExecutor(max_workers=thread) as executor:
        future_to_obj = {executor.submit(
            download_object, bucket, obj, lock, local_dir, pbar, limit_speed_per_thread
        ): obj for obj in obj_info_list}

        for future in as_completed(future_to_obj):
            obj = future_to_obj[future]
            success, _ = future.result()
            if not success:
                error_object_list.append(obj)

    return error_object_list
