#!/usr/bin/env python3
#
# Copyright 2022 Shanghai AI Lab. Licensed under MIT License.
#
import requests
from pathlib import Path
from opendatalab.exception import OpenDataLabAuthenticationError, OpenDataLabError
from opendatalab.utils import bytes2human


class OpenDataLabAPI(object):
    def __init__(self, host, token):
        self.host = host
        self.token = token

    def get_dataset_sts(self, dataset):
        """
        function: get dataset sts by dataset_name
        Args:
            dataset (string): dataset_name

        Raises:
            OpenDataLabError: 

        Returns:
            string: json data from response
        """
        resp = requests.get(
            f"{self.host}/api/datasets/{dataset}/sts",
            headers={"X-OPENDATALAB-API-TOKEN": self.token},
        )
        if resp.status_code != 200:
            raise OpenDataLabError(resp.status_code, resp.text)
        return resp.json()["data"]
    
    def login(self, username: str, password: str):
        params = {
            'email': username,
            'password': password
        }
        resp = requests.get(
            f"{self.host}/api/users/login",
            params = params,
            headers={"content-type": "application/json"},
        )
        if resp.status_code != 200:
            raise OpenDataLabAuthenticationError(resp.status_code, resp.text)

        cookies_dict = requests.utils.dict_from_cookiejar(resp.cookies)
        if 'opendatalab_session' in cookies_dict.keys():
            opendatalab_session	= cookies_dict['opendatalab_session']
        else:
            raise OpenDataLabError(resp.status_code, "No opendatalab_session")
        
        config_json = {
            'endpoint': self.host,
            'user.email': username,
            'user.token': opendatalab_session,
            } 
        
        return config_json
        
    
    def ls(self, dataset):
        ds_split = dataset.split("/")
        if len(ds_split) > 1:
            dataset_name = ds_split[0]
            
        resp = requests.get(
            f"{self.host}/api/datasets/{dataset_name}/sts",
            headers={"X-OPENDATALAB-API-TOKEN": self.token},
        )
        if resp.status_code != 200:
            raise OpenDataLabError(resp.status_code, resp.text)
        data = resp.json()["data"]
        
    
    def search_dataset(self, dataset):
        resp = requests.get(
            f"{self.host}/api/datasets/{dataset}/sts",
            headers={"X-OPENDATALAB-API-TOKEN": self.token},
        )
        if resp.status_code != 200:
            raise OpenDataLabError(resp.status_code, resp.text)
        return resp.json()["data"]
    
    def get_info(self, dataset):
        resp = requests.get(
            f"{self.host}/api/datasets/{dataset}",
            headers={"X-OPENDATALAB-API-TOKEN": self.token},
        )
        if resp.status_code != 200:
            raise OpenDataLabError(resp.status_code, resp.text)
        data =  resp.json()["data"]
        info_data = {
            'id': data['id'],
            'name': data['name'],
            'fileBytes': bytes2human(data['fileBytes']),
            'fileCount': data['fileCount'],
            'publishDate': data['publishDate'],
            'licenses': data['licenses'],
            'publisher': data['publisher'],
            'labelFileTypes': data['labelFileTypes'],
            'mediaTypes': data['mediaTypes'],
            'labelTypes': data['labelTypes'],            
        }
        
        return info_data