import oss2
import requests

from .api import OpenDataLabAPI
from .utils import parse_url, get_api_token_from_env
from requests.adapters import HTTPAdapter


class Dataset(object):
    def __init__(
        self, url: str, token: str = "", storage_format: str = "source"
    ) -> None:
        host, dataset_id = parse_url(url)
        self.dataset_id = dataset_id
        if token == "":
            token = get_api_token_from_env()
        self.open_data_lab_api = OpenDataLabAPI(host, token)
        self.storage_format = storage_format

        self.oss_bucket = None
        self.oss_path_prefix = ""
        self.init_oss_bucket()

    def get(self, filepath: str):
        object_key = self.get_object_key_prefix() + filepath
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

    def get_oss_bucket(self) -> oss2.Bucket:
        if self.oss_bucket is None:
            self.init_oss_bucket()
        return self.oss_bucket

    def get_object_key_prefix(self, compressed=False, standard_version='0.3') -> str:
        if compressed:
            if self.storage_format == "standard":
                # We use 0.3 by default.
                return f"{self.oss_path_prefix}/{self.storage_format}_compressed/f{standard_version}/"
            else:
                return f"{self.oss_path_prefix}/{self.storage_format}_compressed/"

        return f"{self.oss_path_prefix}/{self.storage_format}/"

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
