#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2022 Shanghai AI Lab. Licensed under MIT License.
#

"""Client Module"""

from opendatalab.client.client import Client
from opendatalab.cli.config import config

__all__ = [
    "Client",
    "config",
]