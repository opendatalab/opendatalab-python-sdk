#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2022 Shanghai AI Lab. Licensed under MIT License.
#

"""OpenDataLab python SDK."""

from opendatalab.__version__ import __url__, __version__
from opendatalab.client.client import Client

__all__ = ["__url__", "__version__", "Client"]
