#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2022 Shanghai AI Lab. Licensed under MIT License.
#
from opendatalab.cli.utility import ContextInfo, exception_handler
from opendatalab.utils import bytes2human
import click


@exception_handler
def _implement_info(obj: ContextInfo, dataset: str) -> None:
    
    client = obj.get_client()
    odl_api = client.get_api()
    info_data = odl_api.get_info(dataset)
    similar_data_list = odl_api.get_similar_dataset(dataset)

    data_introd = info_data['introduction']
    introduction_str = ""
    if data_introd and len(data_introd) > 0:
        introduction_str = data_introd[:97] + '...'

    license_list = info_data['licenses']
    license_str = ""
    if license_list and len(license_list) > 0:
        license_str = ", ".join([x['name'] for x in license_list])
        
    publisher_list = info_data['publisher']
    publisher_str = ""
    if publisher_list and len(publisher_list) > 0:
        publisher_str = ", ".join([x['name'] for x in publisher_list])
        
    mediaTypes_list = info_data['mediaTypes']
    mediaTypes_str = ""
    if mediaTypes_list and len(mediaTypes_list) > 0:
        mediaTypes_str = ", ".join([x['name'] for x in mediaTypes_list])

    labelTypes_list = info_data['labelTypes']
    labelTypes_str = ""
    if labelTypes_list and len(labelTypes_list) > 0:
        labelTypes_str = ", ".join([x['name'] for x in labelTypes_list])
        
    taskTypes_list = info_data['taskTypes']
    taskTypes_str = ""
    if labelTypes_list and len(taskTypes_list) > 0:
        taskTypes_str = ", ".join([x['name'] for x in taskTypes_list])

    tags_list = info_data['tags']
    tags_str = ""
    if tags_list and len(tags_list) > 0:
        tags_str = ", ".join([x['name'] for x in tags_list])


    citation_data = info_data['citation']
    citation_str = ""
    if citation_data and len(citation_data) > 0:
        citation_str = citation_data.replace('\r','').replace('\n','')


    simliar_ds_str = ""
    if similar_data_list and len(similar_data_list) > 0:
        simliar_ds_str = ", ".join([x['name'] for x in similar_data_list])
                 
    info_data = {
        'Name': info_data['name'],
        'File Bytes': bytes2human(info_data['fileBytes']),
        'File Count': info_data['fileCount'],
        'Introduction': introduction_str,
        'Issue Time': info_data['publishDate'],
        'License': license_str,
        'Author': publisher_str,
        'Data Type': mediaTypes_str,
        'Label Type': labelTypes_str,   
        'Task Type' : taskTypes_str,
        'Tags' : tags_str,
        'HomePage' : info_data['pulishUrl'],
        'Citation' : citation_str,
        'Similar Datasets': simliar_ds_str,         
    }
    
    print("====="*8)
    for key in sorted(info_data.keys()):
        val = info_data[key]
        val = "" if not val else val
        click.echo('{:<30}{:<100}'.format(key, val))
        # print('{:<30}{:<100}'.format(key, val))
