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
import os
from typing import TextIO

import yaml
try:
    from yaml import CSafeLoader as SafeLoader
except ImportError:
    from yaml import SafeLoader

from . import command_builder, command_runner
from .config_readers import HierarchicalConfigReader, SimpleConfigReader
from .exceptions import ConfigLoadError
from .parser import ParserBuilder
from .models import CompletedCommand

class YamlRunner():
    """YamlRunner class for executing commands from a YAML configuration file.

    This class provides a framework for running commands defined within a YAML
    configuration file. It processes a YAML configuration and sets up argument
    parsers, allowing the commands from the yaml to be executed..
    """

    def __init__(self,
                 config:dict|io.IOBase|str,
                 program:str='',
                 hierarchical: bool=False,
                 fail_fast=True,
                 parser_class:type[argparse.ArgumentParser]=argparse.ArgumentParser):
        """Initiate a YamlRunner object

        Args:
            config (dict | io.IOBase | str): Yaml configuration of commands that can be run.
            program (str, Optional): Program name. Defaults to an empty string.
            hierarchical (bool, Optional): Process the yaml hierarchically. Defaults to False.
            fail_fast (bool, Optional): Prevent command list from continuing after a command has failed.
                                        Defaults to True.
        """
        if hierarchical:
            self._config_reader_class = HierarchicalConfigReader
        else:
            self._config_reader_class = SimpleConfigReader

        self._program = program
        self._fail_fast = fail_fast
        self._parser_builder = ParserBuilder(parser_class, program)
        self.config = config

    @property
    def config(self) -> dict:
        """A copy of the config currently in use by the YamlRunner"""
        return self._config_reader.config

    @config.setter
    def config(self, config: dict|io.IOBase|str):
        config_dict = self._config_to_dict(config)

        reader = self._config_reader_class(config_dict)
        commands = reader.get_commands()
        parser = self._parser_builder.build(commands)

        self._config_reader = reader
        self._parser = parser

    def _load_yaml(self, stream: TextIO):
        try:
            return yaml.load(stream, SafeLoader)
        except yaml.YAMLError as e:
            raise ConfigLoadError(f"Failed to parse YAML config: {e}") from e

    def _load_yaml_file(self, file_path: str):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return self._load_yaml(f)
        except FileNotFoundError as e:
            raise ConfigLoadError(f"Failed to find config file {file_path}") from e

    def _config_to_dict(self, config: dict|io.IOBase|str) -> dict:
        """Processes the incoming config and returns the dictionary

        Args:
            config (dict | io.IOBase | str): A config to be process, either already parsed
                as a dictionary, as an open file or as a string path to the file.

        Raises:
            ConfigLoadError: When config is not a valid type.

        Returns:
            dict: Config in dictionary form.
        """
        if isinstance(config, str):
            return self._load_yaml_file(config)
        elif isinstance(config, io.IOBase):
            config.seek(0)
            return self._load_yaml(config)
        elif isinstance(config, dict):
            return config
        else:
            raise ConfigLoadError(
                f'Config argument must of type IO, str or dict. Got type: [{type(config)}]')

    def run(self, args: list[str], config: dict|io.IOBase|str = None) -> list[CompletedCommand]:
        """
        This function runs a script with specified configuration and arguments,
        processing command line arguments and executing commands.

        Args:
            args (list): The arguments passed to the script.
            config (dict|io.IOBase|str): Yaml configuration of commands that can be run.
                Defaults to None. If None, config comes from class self attributes.

        Returns:
            list[CompletedCommand]: Returns a list of information about each command
                completed by yaml_runner.
        """
        if config is not None:
            self.config = config

        if completion_env := os.getenv('_YAML_RUNNER_COMPLETE'):
            completion = self._parser.get_completion(completion_env)
            print('\n'.join(completion))
            return [CompletedCommand(0, '', '')]
        else:
            parsed_command = self._parser.parse(args)
            built_commands = command_builder.build_commands(parsed_command)
            return command_runner.run_commands(built_commands, self._fail_fast)

    def get_completion(self, completion_shell: str):
        self._parser.get_completion(completion_shell)
