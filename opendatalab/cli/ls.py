#
# Copyright 2022 Shanghai AI Lab. Licensed under MIT License.
#
import oss2

from opendatalab.cli.utility import ContextInfo, exception_handler
from opendatalab.utils import bytes2human


@exception_handler
def implement_ls(obj: ContextInfo, dataset: str) -> None:
    client = obj.get_client()

    ds_split = dataset.split("/")
    if len(ds_split) > 1:
        dataset_name = ds_split[0]
        sub_dir = "/".join(ds_split[1:])
    else:
        dataset_name = dataset
        sub_dir = ""
    dataset_instance = client.get_dataset(dataset_name=dataset_name)
    bucket = dataset_instance.get_oss_bucket()
    prefix = dataset_instance.get_object_key_prefix(compressed=True)

    object_info_dict = {}
    total_files, total_size = 0, 0
    for info in oss2.ObjectIteratorV2(bucket, prefix):
        if not info.is_prefix() and not info.key.endswith("/"):
            file_name = "/".join(info.key.split("/")[2:])
            if not sub_dir:
                object_info_dict[file_name] = bytes2human(info.size)
                total_files = total_files + 1
                total_size = total_size + info.size
            elif sub_dir and file_name.startswith(sub_dir):
                object_info_dict[file_name] = bytes2human(info.size)
                total_files = total_files + 1
                total_size = total_size + info.size
            else:
                pass

    sorted_object_info_dict = dict(sorted(object_info_dict.items(), key=lambda x: x[0], reverse=True))
    print(f"total: {total_files}, size: {bytes2human(total_size)}")
    print('{:<100}\t{:<20}'.format('File Name', 'Size'))
    for key, val in sorted_object_info_dict.items():
        print('{:<100}\t{:<20}'.format(key, val))
