#!/usr/bin/env python3
#
# Copyright 2022 Shanghai AI Lab. Licensed under MIT License.
#
import json
from importlib_metadata import Deprecated
import requests
from opendatalab.exception import *
from opendatalab.utils import bytes2human, UUID
from opendatalab.__version__ import __version__
from opendatalab.client.uaa import get_odl_token


class OpenDataLabAPI(object):
    def __init__(self, host, token, odl_cookie):
        self.host = host
        self.token = token
        self.odl_cookie = odl_cookie

    def get_dataset_sts(self, dataset, expires=3600):
        """Get dataset sts by dataset_name
        Args:
            expires (int): expire timeout unit seconds
            dataset (string): dataset_name

        Raises:
            OpenDataLabError: 

        Returns:
            string: json data from response
        """
        data = {"expires": expires}
        data = json.dumps(data)
        resp = requests.get(
            url=f"{self.host}/api/datasets/{dataset}/sts",
            data=data,
            headers={
                "X-OPENDATALAB-API-TOKEN": self.token,
                "Cookie": f"opendatalab_session={self.odl_cookie}",
                "User-Agent": UUID,
            },
        )
        if resp.status_code != 200:
            raise OpenDataLabError(resp.status_code, resp.text)

        return resp.json()["data"]

    @DeprecationWarning
    def login(self, username: str, password: str):
        data = {
            "email": username,
            "password": password,
        }
        data = json.dumps(data)
        resp = requests.post(
            f"{self.host}/api/users/login",
            data=data,
            headers={"Content-Type": "application/json"},
        )
        if resp.status_code != 200:
            raise OdlAuthError(resp.status_code, resp.text)

        cookies_dict = requests.utils.dict_from_cookiejar(resp.cookies)

        if 'opendatalab_session' in cookies_dict.keys():
            opendatalab_session = cookies_dict['opendatalab_session']
        else:
            raise OpenDataLabError(resp.status_code, "No opendatalab_session")

        config_json = {
            'user.email': username,
            'user.token': opendatalab_session,
        }

        return config_json

    def search_dataset(self, keywords):
        resp = requests.get(
            f"{self.host}/api/datasets/?pageSize=25&keywords={keywords}",
            headers={"X-OPENDATALAB-API-TOKEN": self.token,
                     "Cookie": f"opendatalab_session={self.odl_cookie}",
                     "User-Agent": f"opendatalab-python-sdk/{__version__}",
                     },
        )
        if resp.status_code != 200:
            raise OpenDataLabError(resp.status_code, resp.text)

        result_list = resp.json()["data"]["list"]

        return result_list

    def get_similar_dataset(self, dataset):
        dataset_id = int(self.get_info(dataset)['id'])
        resp = requests.get(
            f"{self.host}/api/datasets/{dataset_id}/similar",
            headers={"X-OPENDATALAB-API-TOKEN": self.token,
                     "Cookie": f"opendatalab_session={self.odl_cookie}",
                     "User-Agent": f"opendatalab-python-sdk/{__version__}",
                     },
        )
        if resp.status_code != 200:
            raise OpenDataLabError(resp.status_code, resp.text)

        data = resp.json()['data']
        return data

    def get_info(self, dataset):
        resp = requests.get(
            f"{self.host}/api/datasets/{dataset}",
            headers={"X-OPENDATALAB-API-TOKEN": self.token,
                     "Cookie": f"opendatalab_session={self.odl_cookie}",
                     "User-Agent": f"opendatalab-python-sdk/{__version__}",
                     },
        )
        if resp.status_code != 200:
            raise OpenDataLabError(resp.status_code, resp.text)

        data = resp.json()["data"]

        return data

    def call_download_log(self, dataset, download_info):
        dataset_id = int(self.get_info(dataset)['id'])
        data = json.dumps(download_info)

        resp = requests.post(
            f"{self.host}/api/track/datasets/download/{dataset_id}",
            data=data,
            headers={"Content-Type": "application/json",
                     "Cookie": f"opendatalab_session={self.odl_cookie}",
                     "User-Agent": f"opendatalab-python-sdk/{__version__}",
                     },
        )

        if resp.status_code != 200:
            raise OpenDataLabError(resp.status_code, resp.text)

    def odl_auth(self, account, password):
        code = get_odl_token(account, password)
        data = {
            "code": code,
            "redirect": "",
        }
        data = json.dumps(data)

        resp = requests.post(
            f"{self.host}/api/users/auth",
            data=data,
            headers={"Content-Type": "application/json"},
        )

        if resp.status_code != 200:
            raise OdlAuthError(resp.status_code, resp.text)

        odl_token = resp.json()["data"]["token"]
        config_json = {
            'user.email': account,
            'user.token': odl_token,
        }

        print(f"odl_token: {odl_token}")
        return config_json
