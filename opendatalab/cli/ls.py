#
# Copyright 2022 Shanghai AI Lab. Licensed under MIT License.
#
from turtle import width
import oss2

from opendatalab.cli.utility import ContextInfo, exception_handler
from opendatalab.utils import bytes2human

@exception_handler
def _implement_ls(obj: ContextInfo, dataset: str) -> None:
    
    client = obj.get_client()
    
    ds_split = dataset.split("/")
    if len(ds_split) > 1:
        dataset_name = ds_split[0]
    else:
        dataset_name = dataset
    
    dataset_instance = client.get_dataset(dataset_name=dataset_name)
    bucket = dataset_instance.get_oss_bucket()
        
    if dataset.endswith("/"):
        ds_path_prefix = dataset
    else:
        ds_path_prefix = dataset + '/'

    prefix = dataset_instance.get_object_key_prefix()
    # print(f"ls prefix: {prefix}")
    object_info_dict = {}
    for info in oss2.ObjectIteratorV2(bucket, prefix):
        if not info.is_prefix() and not info.key.endswith("/"):
            # print(f"file_key: {info.key}")
            file_name = "/".join(info.key.split("/")[2:])
            object_info_dict[file_name] = bytes2human(info.size)
            
    sorted_object_info_dict = dict(sorted(object_info_dict.items(), key=lambda x: x[0], reverse=True))
    print('{:<100}\t{:<20}'.format('FILE', 'SIZE'))
    for key, val in sorted_object_info_dict.items():
        print('{:<100}\t{:<20}'.format(key, val))