import pytest

import opendatalab


def test_dataset():
    dataset = opendatalab.Dataset(url="http://opendatalab-test3.shlab.tech/datasets/4")
    print(dataset.get("t10k-images-idx3-ubyte"))
    print("ok")


def test_select_endpoint():
    dataset = opendatalab.Dataset(url="http://opendatalab-test3.shlab.tech/datasets/4")
    endpoint = dataset.select_endpoint(
        {
            "endpoint": {
                "vpc": "https://oss-cn-shanghai.aliyuncs.com",
                "internet": "https://foo-cn-shanghai.foo.com/",
            }
        }
    )
    assert endpoint == "https://oss-cn-shanghai.aliyuncs.com"

    endpoint = dataset.select_endpoint(
        {
            "endpoint": {
                "vpc": "https://oss-cn-shanghai-internal.aliyuncs.com",
                "internet": "https://oss-cn-shanghai.aliyuncs.com",
            }
        }
    )
    assert endpoint == "https://oss-cn-shanghai.aliyuncs.com"


def test_client():
    client = opendatalab.Client(host="http://opendatalab-test3.shlab.tech")
    print(client.get(4, "t10k-images-idx3-ubyte"))
