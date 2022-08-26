#!/usr/bin/env python3
#
# Copyright 2022 Shanghai AI Lab. Licensed under MIT License.
#
import os
from pathlib import Path


class Config:
    def __init__(self) -> None:
        conf_file = self._get_config_filepath()
        self.conf_file = conf_file

    @staticmethod
    def _get_config_filepath() -> str:
        """Get the path of the config file.
        
        Returns:  The config file path.
        """
        odl_conf = os.path.join(os.path.expanduser("~"), ".opendatalab", "config.json")
        conf_dir = Path(odl_conf).parent
        if not Path(conf_dir).exists():
            conf_dir.mkdir(parents=True)

        if not Path(odl_conf).exists():
            Path(odl_conf).touch(exist_ok=True)

        return odl_conf


config = Config()
