#!/usr/bin/env python3
#
# Copyright 2022 Shanghai AI Lab. Licensed under MIT License.
#
from opendatalab.__version__ import __url__
from opendatalab.client.api import OpenDataLabAPI
from opendatalab.dataset.dataset import Dataset
from opendatalab.utils import get_api_token_from_env


class Client:
    def __init__(self, host: str = __url__, token: str = "", odl_cookie: str = ""):
        """opendatalab client

        Args:
            host str: "https://opendatalab.org.cn".
            token str: Defaults to "".
            odl_cookie str: Defaults to "".
        """
        self.host = host
        self.token = token
        self.odl_cookie = odl_cookie
        if self.token == "":
            self.token = get_api_token_from_env()
        self.dataset_map = {}
        self.odl_api = None

    def get_dataset(self, dataset_name: str) -> Dataset:
        if dataset_name not in self.dataset_map:
            self.dataset_map[dataset_name] = Dataset(
                f"{self.host}/datasets/{dataset_name}", self.token, self.odl_cookie)
        return self.dataset_map[dataset_name]

    def get_api(self):
        self.odl_api = OpenDataLabAPI(self.host, self.token, self.odl_cookie)
        return self.odl_api
