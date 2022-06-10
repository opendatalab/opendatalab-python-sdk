#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2022 Shanghai AI Lab. Licensed under MIT License.
#
from opendatalab.cli.utility import ContextInfo, exception_handler
from opendatalab.utils import bytes2human


@exception_handler
def _implement_info(obj: ContextInfo, dataset: str) -> None:
    
    client = obj.get_client()
    odl_api = client.get_api()
    data = odl_api.get_info(dataset)

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
        
    data_introd = data['introduction']
    introduction_str = ""
    if data_introd and len(data_introd) > 0:
        introduction_str = data_introd[:97] + '...'
                 
    info_data = {
        'id': data['id'],
        'name': data['name'],
        'fileBytes': bytes2human(data['fileBytes']),
        'fileCount': data['fileCount'],
        'introduction': introduction_str,
        'publishDate': data['publishDate'],
        'licenses': license_str,
        'publisher': publisher_str,
        'labelFileTypes': labelFileTypes_str,
        'mediaTypes': mediaTypes_str,
        'labelTypes': labelTypes_str,            
    }
    
    print("====="*8)
    for key, val in info_data.items():
        val = "" if not val else val
        print('{:<30}{:<100}'.format(key.capitalize(), val))
