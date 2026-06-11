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
import os
import pathlib
import sys

import yaml
try:
    from yaml import CSafeLoader as SafeLoader
except ImportError:
    from yaml import SafeLoader

from yaml_runner import YamlRunner
from .yaml_runner_completion import get_completion


class cli():
    def __init__(self):
        parser = argparse.ArgumentParser('yaml_runner', add_help=False, exit_on_error=False)
        parser.add_argument('--config', '-c',
                                  help='Yaml config to read from.',
                                  dest='config',
                                  action='store',
                                  required=True,
                                  nargs=1)
        if completion_env := os.getenv('_YAML_RUNNER_COMPLETE'):
            cwords = os.getenv('COMP_WORDS','').replace('yaml_runner', '', 1)
            if len(cwords.split()) == 1:
                print('\n'.join(get_completion(parser,completion_env)))
                raise SystemExit(0)
            else:
                if '-c' not in cwords:
                    raise SystemExit(0)
                else:
                    cwords = cwords.replace('--config', '', 1)
                    cwords = cwords.replace('-c', '', 1)
        try:
            cli_args, yaml_args = parser.parse_known_args()
        except argparse.ArgumentError as e:
            if completion_env:
                raise SystemExit(0)
            else:
                print(e.message)
                parser.print_help()
                raise SystemExit(2)

        if pathlib.Path(cli_args.config[0]).exists():
            with open(cli_args.config[0],'r',encoding='utf-8') as cfg_file:
                cfg = yaml.load(cfg_file,SafeLoader)
            if cfg is None:
                raise RuntimeError(f'File {cli_args.config[0]} is empty.')
            yr_config = cfg.pop('yaml_runner',{})
            yr_settings = self._get_yr_settings(yr_config)
            if completion_env:
                os.environ['COMP_WORDS'] = cwords.replace(cli_args.config[0],'')
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

def install():
    if os.getenv('SHELL') == '/bin/bash':
        user_home = pathlib.Path().home()
        my_path = pathlib.Path(__file__)
        my_dir = my_path.parent
        os.makedirs(user_home.joinpath('.bash_completion.d'), exist_ok=True)
        with open(my_dir.joinpath('../../data/yaml_runner_bash_completion.sh')) as in_file, \
             open(user_home.joinpath('.bash_completion.d/yaml_runner_bash_completion'),'w') as out_file:
            out_file.write(in_file.read())
        if (bashrc:=pathlib.Path.home().joinpath(pathlib.Path('.bashrc'))).exists():
            _append_to_rcfile(bashrc)
        elif (bash_profile:=pathlib.Path.home().joinpath(pathlib.Path('.bash_profile'))).exists():
            _append_to_rcfile(bash_profile)
        else:
            raise FileNotFoundError('No bash rc file found to append completion source line to.')

def _append_to_rcfile(rcfile:pathlib.Path):
    user_home = rcfile.parent
    source_line = f'\n#YAML_RUNNER COMPLETION\nsource {user_home.joinpath(".bash_completion.d/yaml_runner_bash_completion")}\n'
    if rcfile.exists():
        with open(rcfile,'r',encoding='utf-8') as rcfile_read:
            if source_line not in rcfile_read.read():
                with open(rcfile,'a',encoding='utf-8') as rcfile_append:
                    rcfile_append.write(f'\n{source_line}\n')

if __name__ == '__main__':
    main()