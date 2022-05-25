import requests
from .exceptions import OpenDatalabError


class OpenDataLabAPI(object):
    def __init__(self, host, token):
        self.host = host
        self.token = token

    def get_dataset_sts(self, dataset):
        """
        function: get dataset sts by dataset_name or dataset_id
        Args:
            dataset (string): dataset_name or dataset_id

        Raises:
            OpenDatalabError: 

        Returns:
            string: json data from response
        """
        resp = requests.get(
            f"{self.host}/api/datasets/{dataset}/sts",
            headers={"X-OPENDATALAB-API-TOKEN": self.token},
        )
        if resp.status_code != 200:
            raise OpenDatalabError(resp.status_code, resp.text)
        return resp.json()["data"]
