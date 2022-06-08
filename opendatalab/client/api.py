#!/usr/bin/env python3
#
# Copyright 2022 Shanghai AI Lab. Licensed under MIT License.
#
import json
from sys import prefix
import click
import requests
import oss2
from pathlib import Path
from opendatalab.exception import OpenDataLabAuthenticationError, OpenDataLabError
from opendatalab.utils import bytes2human


class OpenDataLabAPI(object):
    def __init__(self, host, token):
        self.host = host
        self.token = token

    def get_dataset_sts(self, dataset):
        """Get dataset sts by dataset_name
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
        data = {
            "email": username,
            "password": password,
        }
        data = json.dumps(data)
        resp = requests.post(
            f"{self.host}/api/users/login",
            data = data,
            headers={"Content-Type": "application/json"},
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
                    
    
    def search_dataset(self, dataset):
        resp = requests.get(
            f"{self.host}/api/datasets/?pageSize=25&keywords={dataset}",
            headers={"X-OPENDATALAB-API-TOKEN": self.token},
        )
        if resp.status_code != 200:
            raise OpenDataLabError(resp.status_code, resp.text)
        result_list = resp.json()["data"]["list"]
        print('{:<10}{:<30}{:<10}{:<100}\t{:<10}'.format('Index', 'Name', 'FileSize', 'Description', 'DownloadCount'))

        if result_list:
            for i, res in enumerate(result_list):
                index = i
                ds_name = res['name']
                ds_desc = res['introductionText'][:97] + '...'
                ds_dw_cnt = res['downloadCount']
                ds_file_bytes = bytes2human(res['fileBytes'])
                print('{:<10}{:<30}{:<10}{:<100}\t{:<10}'.format(index, ds_name, ds_file_bytes, ds_desc, ds_dw_cnt))
        
        return result_list

    
    def get_info(self, dataset):
        resp = requests.get(
            f"{self.host}/api/datasets/{dataset}",
            headers={"X-OPENDATALAB-API-TOKEN": self.token},
        )
        if resp.status_code != 200:
            raise OpenDataLabError(resp.status_code, resp.text)
        data =  resp.json()["data"]
        
        license_list = data['licenses']
        license_str = ""
        if license_list and len(license_list) > 0:
            license_str = ", ".join([x['name'] for x in license_list])
        
        publisher_list = data['publisher']
        publisher_str = ""
        if publisher_list and len(publisher_list) > 0:
            publisher_str = ", ".join([x['name'] for x in publisher_list])
        
        labelFileTypes_list = data['labelFileTypes']
        labelFileTypes_str = ""
        if labelFileTypes_list and len(labelFileTypes_list) > 0:
            labelFileTypes_str = ", ".join([x['name'] for x in labelFileTypes_list])
        
        mediaTypes_list = data['mediaTypes']
        mediaTypes_str = ""
        if mediaTypes_list and len(mediaTypes_list) > 0:
            mediaTypes_str = ", ".join([x['name'] for x in mediaTypes_list])

        labelTypes_list = data['labelTypes']
        labelTypes_str = ""
        if labelTypes_list and len(labelTypes_list) > 0:
            labelTypes_str = ", ".join([x['name'] for x in labelTypes_list])
                 
        info_data = {
            'id': data['id'],
            'name': data['name'],
            'fileBytes': bytes2human(data['fileBytes']),
            'fileCount': data['fileCount'],
            'publishDate': data['publishDate'],
            'licenses': license_str,
            'publisher': publisher_str,
            'labelFileTypes': labelFileTypes_str,
            'mediaTypes': mediaTypes_str,
            'labelTypes': labelTypes_str,            
        }
        # print(json.dumps(info_data, indent=4, sort_keys=True))
                
        return info_data