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
import io
import subprocess
import re
import sys
import threading

import yaml
try:
    from yaml import CSafeLoader as SafeLoader
except ImportError:
    from yaml import SafeLoader

from .base_engine import BaseYamlRunnerEngine

class HierarchicalEngine(BaseYamlRunnerEngine):

    def _strip_config(self, parsed_config: dict, nested: bool=False) -> dict:
        """
        Recursively strip the dict down to trees that contain commands.
        
        Args:
            parsed_config (dict): Dictionary containing command configuration data.
            nested (bool): True if the function is being called in a recursive loop.
        
        Returns:
            dict: Config dictionary containing only sections with commands.
        """
        command_dicts = parsed_config.copy()
        for key, value in parsed_config.items():
            if key == 'description' and nested:
                continue
            elif key == 'command' and nested:
                command_dicts.update({key: value})
            elif isinstance(value,dict):
                check = self._strip_config(value,nested=True)
                check_keys = list(check.keys())
                if check and check_keys != ['description']:
                    command_dicts.update({key:value})
                else:
                    command_dicts.pop(key)
            else:
                command_dicts.pop(key)
        return command_dicts

    def _setup_parsers(self):
        command_dicts = self._strip_config(self._config)
        subparsers = self._arg_parser.add_subparsers(dest='command_name',
                                                     required=True)
        self._setup_subparsers(command_dicts, subparsers)

    def _setup_subparsers(self, nested_cmds:dict, subparsers: argparse._SubParsersAction):
        """
        Recursively sets up subparsers for the nested commands in the dict.

        Sets up subparser for the top keys in the dict. If a command is found under the key
        the commands params are added to the subparser. Otherwise, the nested dict is passed
        into the next call of this functions. The key 'description' is ignored, to prevent
        the description of a subcommand from being added as a subcommand itself.

        Args:
            nested_cmds (dict): Dictionary of nested commands.
            subparsers (argparse._SubParsersAction): The main argument parsers subparser object.
        """
        for key, value in nested_cmds.items():
            if key == 'description':
                continue
            command_parser = subparsers.add_parser(key,
                                    help=value.get('description',''))
            if value.get('command'):
                params = value.get('params')
                if params:
                    self._add_params_parser(command_parser,params)
            else:
                command_subparsers = command_parser.add_subparsers(dest='command_name', required=True)
                self._setup_subparsers(value,command_subparsers)
