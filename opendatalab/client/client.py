#!/usr/bin/env python3
#
# Copyright 2022 Shanghai AI Lab. Licensed under MIT License.
#
from opendatalab.dataset.dataset import Dataset
from opendatalab.utils import get_api_token_from_env


class Client:
    def __init__(self, host: str = "http://opendatalab-test2.shlab.tech", token: str = ""):
        """_summary_

        Args:
            host str:  Defaults to "https://opendatalab.com/".
            token str: Defaults to "".
        """
        self.host = host
        self.token = token
        if self.token == "":
            self.token = get_api_token_from_env()
        self.dataset_map = {}

    def get_dataset(self, dataset_name: str) -> Dataset:
        if dataset_name not in self.dataset_map:
            self.dataset_map[dataset_name] = Dataset(
                f"{self.host}/datasets/{dataset_name}", self.token)
        return self.dataset_map[dataset_name]

    def get(self, dataset_name: int, filepath: str):
        dataset = self.get_dataset(dataset_name)
        return dataset.get(filepath)
