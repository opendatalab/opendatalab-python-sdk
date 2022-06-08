#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2022 Shanghai AI Lab. Licensed under MIT License.
#
from opendatalab.cli.utility import ContextInfo, exception_handler


@exception_handler
def _implement_info(obj: ContextInfo, dataset: str) -> None:
    
    client = obj.get_client()
    odl_api = client.get_api()
    info_data = odl_api.get_info(dataset)
    sort_info_dict = dict(sorted(info_data.items(), key=lambda x: x[0], reverse=False))
    print("====="*8)
    for key, val in sort_info_dict.items():
        val = "" if not val else val
        print('{:<30}{:<100}'.format(key.capitalize(), val))
