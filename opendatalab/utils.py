import os
from urllib.parse import urlparse


def parse_url(url: str) -> (str, str):
    o = urlparse(url)
    host = f"{o.scheme}://{o.hostname}"
    if o.port is not None:
        host += ":" + str(o.port)

    dataset_id = o.path.split("/")[-1]
    return host, dataset_id


def get_api_token_from_env():
    return os.environ.get("OPENDATALAB-API-TOKEN", "")
