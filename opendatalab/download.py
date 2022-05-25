from logging import root
import threading
import click
import oss2
import os

from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed, thread

from .client import Client

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
        headers[oss2.models.OSS_TRAFFIC_LIMIT] = str(limit_speed)
        filename = os.path.join(root, object_info.key.split("/")[-1])
        print(f"\t start downloading file: {filename} ...")
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
    if limit_speed < 245760:
        return 245760
    if limit_speed > 838860800:
        return 838860800
    return limit_speed

@click.group()
def cli():
    """python sdk for opendatalab dataset download
    """

@cli.command()
@click.option(
    "--name",
    "-n",
    default="",
    help="Name of OpenDatalab dataset which you want to download.",
)
@click.option(
    "--root", 
    default=".", help="Local path, default: current working path."
)
@click.option(
    "--thread",
    "-t",
    default=10,
    help="Number of thread for download",
    show_default=True,
)
@click.option(
    "--limit_speed",
    default=0,
    help="Download limit speed: KB/s, 0 is unlimited",
    show_default=True,
)
@click.option(
    "--host",
    default="http://opendatalab-test2.shlab.tech", #  https://opendatalab.com/
    help="OpenDatalab host",
    show_default=True,
)
@click.option(
    "--token",
    default="",
    help="OpenDatalab user api token",
    envvar="OPENDATALAB-API-TOKEN",
)
def download(name, root, thread, limit_speed, host, token):
    cli = Client(host, token)
    dataset = cli.get_dataset(name)
    bucket = dataset.get_oss_bucket()
    prefix = dataset.get_object_key_prefix()
    object_info_list = []
    total_size = 0
    click.echo(f"Scanning file list")
    for info in oss2.ObjectIteratorV2(bucket, prefix):
        object_info_list.append(info)
        total_size += info.size
    click.echo(
        f"Scan file list done, total size: {tqdm.format_sizeof(total_size)}, file numbers: {len(object_info_list)}"
    )

    pbar = tqdm(total=total_size, unit="B", unit_scale=True)
    lock = threading.RLock()
    error_object_list = []
    limit_speed_per_thread = get_oss_traffic_limit(int(limit_speed * 1024 * 8 / thread))
    with ThreadPoolExecutor(max_workers=thread) as executor:
        future_to_obj = {
            executor.submit(
                download_object, bucket, obj, lock, root, pbar, limit_speed_per_thread
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


# if __name__ == "__main__":
#     name = 'FB15k'
#     root = os.path.join(os.curdir,'output')
#     thread = 2
#     limit_speed = 0
#     host = 'http://opendatalab-test2.shlab.tech'
#     token = ""

#     download(name,root,thread, limit_speed,host,token)
