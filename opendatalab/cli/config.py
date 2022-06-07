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

    
    def write_config(self, content: str) -> bool:
        with open(self.conf_file, 'w') as fd:
            fd.write(content + '\n')
            
        return True
    
    def clean_config(self) -> bool:
        with open(self.conf_file, "r+") as f:
            f.seek(0)
            f.truncate()
            
        return True
    
    @staticmethod
    def _get_config_filepath() -> str:
        """
        Get the path of the config file.
        Returns:
            The path of the config file.
        """
        odl_conf = os.path.join(os.path.expanduser("~"), ".opendatalab", "config.json")
        conf_dir = Path(odl_conf).parent
        if not Path(conf_dir).exists():
            conf_dir.mkdir(parents=True)
            if not Path(odl_conf).exists():
                Path(odl_conf).touch(exist_ok=True)
            
        return odl_conf  
            
config = Config()