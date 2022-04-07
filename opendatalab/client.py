import os

from .dataset import Dataset


class Client:
    def __init__(self, host: str = "https://opendatalab.com/", token: str = ""):
        self.host = host
        self.token = token
        if self.token == "":
            self.token = os.environ.get("OPENDATALAB-API-TOKEN", "")
        self.dataset_map = {}

    def get(self, dataset_id: int, filepath: str, storage_format: str = "source"):
        if dataset_id not in self.dataset_map:
            self.dataset_map[dataset_id] = Dataset(
                f"{self.host}/datasets/{dataset_id}", self.token, storage_format
            )
        dataset = self.dataset_map[dataset_id]
        return dataset.get(filepath)
