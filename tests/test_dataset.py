import pytest

import opendatalab


def test_dataset():
    dataset = opendatalab.Dataset(url="http://opendatalab-test3.shlab.tech/datasets/4")
    print(dataset.get(""))
    print("ok")
