import oss2
import requests

from urllib.parse import urlparse
from .api import OpenDataLabAPI
from requests.adapters import HTTPAdapter


def parse_url(url: str) -> (str, str):
    o = urlparse(url)
    host = f"{o.scheme}://{o.hostname}"
    if o.port is not None:
        host += ":" + str(o.port)

    dataset_id = o.path.split("/")[-1]
    return host, dataset_id


class Dataset(object):
    def __init__(
        self, url: str, token: str = "", storage_format: str = "source"
    ) -> None:
        host, dataset_id = parse_url(url)
        self.dataset_id = dataset_id
        self.open_data_lab_api = OpenDataLabAPI(host, token)
        self.storage_format = storage_format

        self.oss_bucket = None
        self.oss_path_prefix = ""
        self.init_oss_bucket()

    def get(self, filepath: str):
        object_key = f"{self.oss_path_prefix}/{self.storage_format}/" + filepath
        try:
            return self.oss_bucket.get_object(object_key)
        except oss2.exceptions.ServerError as e:
            if "InvalidAccessKeyId" not in str(e):
                raise e

            self.init_oss_bucket()
            return self.oss_bucket.get_object(object_key)

    def init_oss_bucket(self):
        sts = self.open_data_lab_api.get_dataset_sts(self.dataset_id)
        auth = oss2.StsAuth(
            sts["accessKeyId"], sts["accessKeySecret"], sts["securityToken"]
        )
        path_info = sts["path"].replace("oss://", "").split("/")
        bucket_name = path_info[0]
        self.oss_bucket = oss2.Bucket(auth, self.select_endpoint(sts), bucket_name)
        self.oss_path_prefix = "/".join(path_info[1:])

    @classmethod
    def select_endpoint(cls, sts):
        try:
            s = requests.Session()
            vpc_endpoint = sts["endpoint"]["vpc"]
            s.mount(vpc_endpoint, HTTPAdapter(max_retries=0))
            s.get(vpc_endpoint, timeout=(0.5, 1))
            return vpc_endpoint
        except requests.exceptions.ConnectTimeout or requests.exceptions.ReadTimeout:
            return sts["endpoint"]["internet"]
