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

class SimpleEngine(BaseYamlRunnerEngine):
    """YamlRunner class for executing commands from a YAML configuration file.

    This class provides a framework for running commands defined within a YAML
    configuration file. It allows for parsing arguments from the command line,
    processing the YAML configuration, and executing the defined commands.

    Attributes:
        _arg_parser (argparse.ArgumentParser): The main argument parser for the script.
    """

    def _setup_parsers(self):
        command_dicts = self._get_command_sections(self._config)
        subparsers = self._arg_parser.add_subparsers(dest='command_name',
                                                     required=True)
        for command_dict in command_dicts:
            params = command_dict.get('params')
            command_parser = subparsers.add_parser(command_dict.get('name'),
                                                   help=command_dict.get('description',''))
            if params:
                self._add_params_parser(command_parser, params)
