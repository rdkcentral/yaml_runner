#!/usr/bin/env python3
#** *****************************************************************************
# *
# * If not stated otherwise in this file or this component's LICENSE file the
# * following copyright and licenses apply:
# *
# * Copyright 2024 RDK Management
# *
# * Licensed under the Apache License, Version 2.0 (the "License");
# * you may not use this file except in compliance with the License.
# * You may obtain a copy of the License at
# *
# *
# http://www.apache.org/licenses/LICENSE-2.0
# *
# * Unless required by applicable law or agreed to in writing, software
# * distributed under the License is distributed on an "AS IS" BASIS,
# * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# * See the License for the specific language governing permissions and
# * limitations under the License.
# *
#* ******************************************************************************

import argparse
import pathlib
import sys
from os import path

import yaml
try:
    from yaml import CSafeLoader as SafeLoader
except ImportError:
    from yaml import SafeLoader

# When running as script, need to handle imports properly
if __name__ == '__main__' and __package__ is None:
    # Add src directory to path
    sys.path.insert(0, path.dirname(path.dirname(path.abspath(__file__))))
    # Set package name for relative imports to work
    __package__ = 'yaml_runner'

# Now do the import - will use relative imports within yaml_runner package
if __package__:
    from .yaml_runner import YamlRunner
else:
    from yaml_runner import YamlRunner

class cli():
    def __init__(self):
        parser = argparse.ArgumentParser('yaml_runner', add_help=False)
        parser.add_argument('--config', '-c',
                                  help='Yaml config to read from.',
                                  dest='config',
                                  action='store',
                                  required=True,
                                  nargs=1)
        try:
            cli_args, yaml_args = parser.parse_known_args()
        except SystemExit as e:
            parser.print_help()
            raise

        if pathlib.Path(cli_args.config[0]).exists():
            with open(cli_args.config[0],'r',encoding='utf-8') as cfg_file:
                cfg = yaml.load(cfg_file,SafeLoader)
            if cfg is None:
                raise RuntimeError(f'File {cli_args.config[0]} is empty.')
            yr_config = cfg.pop('yaml_runner',{})
            yr_settings = self._get_yr_settings(yr_config)
            yr = YamlRunner(cfg,
                            program='yaml_runner',
                            **yr_settings)
            _,_,exit_code = yr.run(yaml_args)
            raise SystemExit(sorted(exit_code)[-1])
        else:
            raise FileNotFoundError(cli_args.config[0])

    def _get_yr_settings(self,global_cfg:dict) -> dict:
        """
        Parses the yaml_runner section of the config to setup
        a kwarg dict with the relevant options.

        Args:
            global_cfg (dict): yaml_runner section from yaml config.

        Returns:
            dict: kwarg dict to use with yaml_runner initialisation.
        """
        settings = {}
        if global_cfg.get('hierarchical',False) is True:
            settings.update({'hierarchical' : True})
        if global_cfg.get('fail_fast',True) is False:
            settings.update({'fail_fast':False})
        return settings

def main():
    cli()

if __name__ == '__main__':
    main()