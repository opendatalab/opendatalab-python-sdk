import oss2

from urllib.parse import urlparse
from .api import OpenDataLabAPI


def parse_url(url: str) -> (str, str):
    o = urlparse(url)
    host = f"{o.scheme}://{o.hostname}"
    if o.port is not None:
        host += ":" + str(o.port)

    dataset_id = o.path.split("/")[-1]
    return host, dataset_id


class Dataset(object):
    def __init__(self, url: str, token: str = "") -> None:
        host, dataset_id = parse_url(url)
        self.dataset_id = dataset_id
        self.open_data_lab_api = OpenDataLabAPI(host, token)

    def get(self, key: str):
        sts = self.open_data_lab_api.get_dataset_sts(self.dataset_id)

        auth = oss2.StsAuth(
            sts["accessKeyId"], sts["accessKeySecret"], sts["securityToken"]
        )
        bucket_name = sts["path"].replace("oss://", "").split("/")[0]
        bucket = oss2.Bucket(auth, sts["endpoint"]["internet"], bucket_name)
        return bucket.get_object("MNIST/source/train-labels-idx1-ubyte")
