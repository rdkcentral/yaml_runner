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

import yaml
try:
    from yaml import CSafeLoader as SafeLoader
except ImportError:
    from yaml import SafeLoader

from .command_builder import CommandBuilder
from . import command_runner
from .config_readers import HierarchicalConfigReader, SimpleConfigReader
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
            self._config_reader = SimpleConfigReader

        self._program = program
        self._fail_fast = fail_fast
        self._parser_builder = ParserBuilder(parser_class, program)
        self._command_builder = CommandBuilder()
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

    def _config_to_dict(self, config: dict|io.IOBase|str) -> dict:
        """Processes the incoming config and returns the dictionary

        Args:
            config (dict | io.IOBase | str): A config to be process, either already parsed
                as a dictionary, as an open file or as a string path to the file.

        Raises:
            TypeError: When config is not a valid type.

        Returns:
            dict: Parsed config.
        """
        if isinstance(config,str):
            with open(config, 'r', encoding='utf-8') as f:
                config_dict = yaml.load(f,SafeLoader)
        elif isinstance(config, io.IOBase):
            config.seek(0)
            config_dict = yaml.load(config,SafeLoader)
        elif isinstance(config, dict):
            config_dict = config
        else:
            raise TypeError(
                f'Config argument must of type IO, str or dict. Got type: [{type(config)}]')
        return config_dict

    def run(self, args: list[str], config: dict|io.IOBase|str = None) -> list[CompletedCommand]:
        """
        This function runs a script with specified configuration and arguments, processing command line
        arguments and executing commands.

        Args:
            config (dict|io.IOBase|str): Yaml configuration of commands that can be run. Defaults to None.
                If None, config is expected to be passed in from command line with `--config` option.
            args (list): The arguments passed to the script. Defaults to None.
                If None, external args are processed and used instead.

        Returns:
            tuple: Returns a tuple containing three lists: `stdout_list`, `stderr_list`, and `exit_code_list`.
              Each list contains the respective outputs (stdout, stderr,
              and exit code) of running the command(s) specified in the `self.commands` attribute.
        """
        if config:
            self.config = config

        if completion_env := os.getenv('_YAML_RUNNER_COMPLETE'):
            completion = self._parser.get_completion(completion_env)
            print('\n'.join(completion))
            return [CompletedCommand('', '', 0)]
        else:
            parsed_command = self._parser.parse(args)
            built_commands = self._command_builder.build(parsed_command)
            return command_runner.run_commands(built_commands, self._fail_fast)

    def get_completion(self, completion_shell: str):
        self._parser.get_completion(completion_shell)
