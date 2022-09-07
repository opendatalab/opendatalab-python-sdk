#!/usr/bin/env python3
#
# Copyright 2022 Shanghai AI Lab. Licensed under MIT License.
#
import json
import sys

import click
import requests

from opendatalab.__version__ import __version__
from opendatalab.client.uaa import get_odl_token
from opendatalab.exception import *
from opendatalab.utils import UUID


class OpenDataLabAPI(object):
    def __init__(self, host, token, odl_cookie):
        self.host = host
        self.token = token
        self.odl_cookie = odl_cookie

    def get_dataset_sts(self, dataset, expires=900):
        """Get dataset sts by dataset_name
        Args:
            expires (int): expire timeout unit seconds
            dataset (string): dataset_name

        Raises:
            OpenDataLabError: 

        Returns:
            string: json data from response
        """
        data = {"expires": expires, }
        resp = requests.get(
            url=f"{self.host}/api/datasets/{dataset}/sts",
            params=data,
            headers={
                "X-OPENDATALAB-API-TOKEN": self.token,
                "Cookie": f"opendatalab_session={self.odl_cookie}",
                "User-Agent": UUID,
            }, )

        if resp.status_code != 200:
            if resp.status_code == 404:
                raise OdlDataNotExistsError()
            elif resp.status_code == 401:
                raise OdlAuthError()
            elif resp.status_code == 403:
                raise OdlAccessDeniedError()
            elif resp.status_code == 412:
                raise OdlAccessCdnError()
            elif resp.status_code == 500:
                raise OdlAccessDeniedError()
            else:
                raise RespError(resp_code=resp.status_code, error_msg=resp.reason)
        # print(f"sts api, headers: {resp.headers}, text: {resp.text}")
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
            print(f"{OpenDataLabError(resp.status_code, resp.text)}")
            sys.exit(-1)

        result_list = resp.json()["data"]["list"]
        if not result_list:
            click.secho(f"No datasets matched!", fg='red')
            sys.exit(-1)

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
            # print(f"{(resp.status_code, resp.text)}")
            sys.exit(-1)

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
            click.echo(f"dataset: {dataset}, get info failure, error_code: {resp.status_code}")
            sys.exit(-1)

        data = resp.json()["data"]
        if data['id'] == 0:
            click.secho(f"No dataset: {dataset}", fg='red')
            sys.exit(-1)

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

    def get_download_record(self, dataset):
        dataset_id = int(self.get_info(dataset)['id'])
        resp = requests.get(
            f"{self.host}/api/datasets/{dataset_id}/download",
            headers={"Content-Type": "application/json",
                     "Cookie": f"opendatalab_session={self.odl_cookie}",
                     "User-Agent": f"opendatalab-python-sdk/{__version__}",
                     },
        )

        if resp.status_code != 200:
            raise OpenDataLabError(resp_code=resp.status_code, error_msg=resp.reason)

        data = resp.json()["data"]
        return data

    def submit_download_record(self, dataset, download_data):
        dataset_id = int(self.get_info(dataset)['id'])

        profession = "OTHER" if not download_data['profession'] else download_data['profession']
        purpose = ["OTHER"] if not download_data['purpose'] else download_data['purpose']
        expand = ["OTHER"] if not download_data['expand'] else download_data['expand']
        data = {
            "expand": expand,
            "profession": profession,
            "purpose": purpose
        }
        data = json.dumps(data)

        resp = requests.put(
            f"{self.host}/api/datasets/{dataset_id}/download",
            data=data,
            headers={"Content-Type": "application/json",
                     "Cookie": f"opendatalab_session={self.odl_cookie}",
                     "User-Agent": f"opendatalab-python-sdk/{__version__}",
                     },
        )

        if resp.status_code != 200:
            raise OpenDataLabError(resp_code=resp.status_code, error_msg=resp.reason)

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

        return config_json

    def check_version(self):
        resp = requests.get(
            f"{self.host}/api/sdk/checkVersion",
            headers={"Content-Type": "application/json"},
        )

        if resp.status_code != 200:
            raise OdlAuthError(resp.status_code, error_msg=resp.text)
            sys.exit(-1)

        version_info = resp.json()["data"]
        return version_info
