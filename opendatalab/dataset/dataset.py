#!/usr/bin/env python3
#
# Copyright 2022 Shanghai AI Lab. Licensed under MIT License.
#
import oss2
import requests

from opendatalab.client.api import OpenDataLabAPI
from opendatalab.utils import parse_url, get_api_token_from_env
from requests.adapters import HTTPAdapter


class Dataset(object):
    def __init__(self, url: str, token: str = "", odl_cookie: str= "") -> None:
        # print(f"ds url: {url}, token: {token}")
        host, dataset_name = parse_url(url)
        self.dataset_name = dataset_name
        if token == "":
            token = get_api_token_from_env()
        self.open_data_lab_api = OpenDataLabAPI(host, token, odl_cookie)

        self.oss_bucket = None
        self.oss_path_prefix = ""
        self.init_oss_bucket()

    def get(self, filepath: str):
        object_key = self.get_object_key_prefix() + filepath
        try:
            return self.oss_bucket.get_object(object_key)
        except oss2.exceptions.ServerError as e:
            if "InvalidAccessKeyId" not in str(e):
                raise e

            self.init_oss_bucket()
            return self.oss_bucket.get_object(object_key)

    def init_oss_bucket(self):
        sts = self.open_data_lab_api.get_dataset_sts(self.dataset_name)
        # print(f"ds sts: {sts}")
        auth = oss2.StsAuth(
            sts["accessKeyId"], sts["accessKeySecret"], sts["securityToken"]
        )
        path_info = sts["path"].replace("oss://", "").split("/")
        bucket_name = path_info[0]
        self.oss_bucket = oss2.Bucket(auth, self.select_endpoint(sts), bucket_name)
        self.oss_path_prefix = "/".join(path_info[1:])
        # print(f"test-2-> bucket: {bucket_name}, oss_path_prefix: {self.oss_path_prefix}, oss_bucket: {self.oss_bucket}")

    def get_oss_bucket(self) -> oss2.Bucket:
        if self.oss_bucket is None:
            self.init_oss_bucket()
        return self.oss_bucket

    def get_object_key_prefix(self) -> str:
        return f"{self.oss_path_prefix}/source_compressed/"

    @classmethod
    def select_endpoint(cls, sts):
        try:
            s = requests.Session()
            sts_endpoint = sts["endpoint"]["vpc"]
            s.mount(sts_endpoint, HTTPAdapter(max_retries=0))
            s.get(sts_endpoint, timeout=(0.5, 1))
        
        except Exception as e:
            sts_endpoint = sts["endpoint"]["internet"]
        
        return sts_endpoint
