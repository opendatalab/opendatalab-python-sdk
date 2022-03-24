import requests


class OpenDataLabAPI(object):
    def __init__(self, host, token):
        self.host = host
        self.token = token

    def get_dataset_sts(self, dataset_id):
        resp = requests.get(f"{self.host}/api/datasets/{dataset_id}/sts")
        # TODO: check resp
        return resp.json()["data"]
