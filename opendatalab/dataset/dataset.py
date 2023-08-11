#!/usr/bin/env python3
#
# Copyright 2022 Shanghai AI Lab. Licensed under MIT License.
#
import http
import sys

import click
import requests
from requests.adapters import HTTPAdapter

from opendatalab.client.api import OpenDataLabAPI
from opendatalab.exception import OpenDataLabError
from opendatalab.utils import get_api_token_from_env, parse_url


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