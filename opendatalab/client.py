import os

from .dataset import Dataset
from .utils import get_api_token_from_env


class Client:
    def __init__(self, host: str = "https://opendatalab.com/", token: str = ""):
        self.host = host
        self.token = token
        if self.token == "":
            self.token = get_api_token_from_env()
        self.dataset_map = {}

    def get_dataset(self, dataset_id: int, storage_format: str) -> Dataset:
        if dataset_id not in self.dataset_map:
            self.dataset_map[dataset_id] = Dataset(
                f"{self.host}/datasets/{dataset_id}", self.token, storage_format
            )
        return self.dataset_map[dataset_id]

    def get(self, dataset_id: int, filepath: str, storage_format: str = "source"):
        dataset = self.get_dataset(dataset_id, storage_format)
        return dataset.get(filepath)
