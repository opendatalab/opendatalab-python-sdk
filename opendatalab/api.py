import requests
from .exceptions import OpenDatalabError


class OpenDataLabAPI(object):
    def __init__(self, host, token):
        self.host = host
        self.token = token

    def get_dataset_sts(self, dataset_id):
        resp = requests.get(
            f"{self.host}/api/datasets/{dataset_id}/sts",
            headers={"X-OPENDATALAB-API-TOKEN": self.token},
        )
        if resp.status_code != 200:
            raise OpenDatalabError(resp.status_code, resp.text)
        return resp.json()["data"]
