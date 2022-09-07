#!/usr/bin/env python3
#
# Copyright 2022 Shanghai AI Lab. Licensed under MIT License.
#
import http
import sys

import click
import oss2
import requests
from requests.adapters import HTTPAdapter

from opendatalab.client.api import OpenDataLabAPI
from opendatalab.exception import OpenDataLabError
from opendatalab.utils import parse_url, get_api_token_from_env


class Dataset:
    def __init__(self, url: str, token: str = "", odl_cookie: str = "") -> None:
        host, dataset_name = parse_url(url)
        self.dataset_name = dataset_name
        if token == "":
            token = get_api_token_from_env()
        self.open_data_lab_api = OpenDataLabAPI(host, token, odl_cookie)

        self.oss_bucket = None
        self.bucket_name = None
        self.oss_path_prefix = ""
        self.init_oss_bucket()

    def get(self, filepath: str, compressed: bool = True):
        object_key = self.get_object_key_prefix(compressed) + filepath
        try:
            return self.oss_bucket.get_object(object_key)
        except oss2.exceptions.ServerError as e:
            if "InvalidAccessKeyId" not in str(e):
                raise e

            self.init_oss_bucket()
            return self.oss_bucket.get_object(object_key)

    def init_oss_bucket(self, expires=3600):
        sts = self.open_data_lab_api.get_dataset_sts(self.dataset_name, expires=expires)

        if sts:
            path_info = sts["path"].replace("oss://", "").split("/")
            bucket_name = path_info[0]
            sts_point, sts_use_cname = self.select_endpoint(sts)

            if sts_point:
                auth = oss2.StsAuth(sts["accessKeyId"], sts["accessKeySecret"], sts["securityToken"])
                self.oss_bucket = oss2.Bucket(auth, sts_point, bucket_name, is_cname=sts_use_cname)
                self.oss_path_prefix = "/".join(path_info[1:])
            else:
                raise OpenDataLabError(1001, "access to bucket error")

    def get_oss_bucket(self) -> oss2.Bucket:
        if self.oss_bucket is None:
            self.init_oss_bucket()
        return self.oss_bucket

    def refresh_oss_bucket(self) -> oss2.Bucket:
        self.init_oss_bucket()
        return self.get_oss_bucket()

    def get_object_key_prefix(self, compressed: bool = True) -> str:
        if compressed:
            return f"{self.oss_path_prefix}/raw/"
        else:
            return f"{self.oss_path_prefix}/"

    @classmethod
    def select_endpoint(cls, sts):
        s = requests.Session()
        sts_endpoints = sts["endpoints"]
        path_info = sts["path"].replace("oss://", "").split("/")
        bucket_name = path_info[0]

        # use general endpoint
        if len(sts_endpoints) > 0:
            endpoint = sts_endpoints[-1]
            sts_endpoint = endpoint['url']
            sts_use_cname = endpoint['useCname']

            url_splitter = "://"
            url_split_arr = str(sts_endpoint).split(url_splitter)
            url_prefix = url_split_arr[0]
            url_body = url_split_arr[1]
            check_url = url_prefix + url_splitter + bucket_name + "." + url_body + "/check_connected"
            s.mount(check_url, HTTPAdapter(max_retries=0))

            try:
                resp = s.get(check_url, timeout=(3, 1)) # 0.5
                if resp.status_code == http.HTTPStatus.OK:
                    return sts_endpoint, sts_use_cname
            except Exception as e:
                click.secho(f"ConnectionError occurs, please check network!", fg='red')
                sys.exit(-1)