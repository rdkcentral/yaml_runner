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

from .engines import HierarchicalEngine, SimpleEngine

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
                 arg_parse_formatter:argparse.HelpFormatter=argparse.HelpFormatter):
        """Initiate a YamlRunner object

        Args:
            config (dict | io.IOBase | str): Yaml configuration of commands that can be run.
            program (str, Optional): Program name. Defaults to an empty string.
            hierarchical (bool, Optional): Process the yaml hierarchically. Defaults to False.
            fail_fast (bool, Optional): Prevent command list from continuing after a command has failed.
                                        Defaults to True.

        """
        if hierarchical:
            self._engine = HierarchicalEngine(self._config_to_dict(config),
                                              program=program,
                                              formatter=arg_parse_formatter)
        else:
            self._engine = SimpleEngine(self._config_to_dict(config),
                                        program=program,
                                        formatter=arg_parser_formatter)
        self._program = program
        self._fail_fast = fail_fast
        self.config = config


    @property
    def config(self) -> dict:
        """A copy of the config currently in use by the YamlRunner"""
        return self._config.copy()

    @config.setter
    def config(self,config:dict|io.IOBase|str):
        self._engine.config = self._config_to_dict(config)

    def _config_to_dict(self,config:dict|io.IOBase|str) -> dict:
        """Processes the incoming config and returns the dictionary

        Args:
            config (dict | io.IOBase | str): A config to be process, either already parsed as a dictionary,
                                             as an open file or as a string path to the file.

        Raises:
            TypeError: When config is not a valid type.

        Returns:
            dict: Parsed config.
        """
        if isinstance(config,str):
            with open(config,'r',encoding='utf-8') as f:
                config_dict = yaml.load(f,SafeLoader)
        elif isinstance(config,io.IOBase):
            config.seek(0)
            config_dict = yaml.load(config,SafeLoader)
        elif isinstance(config,dict):
            config_dict = config
        else:
            raise TypeError(f'config argument must of type IO, str or dict. Got type: [{type(config)}]')
        return config_dict


    def _run_command(self,command) -> tuple:
        """Runs a command in the shell, captures both stdout and stderr,
        prints them in real-time, and returns them.

        Args:
            command: A list containing the command and its arguments.

        Returns:
            A tuple containing captured stdout (bytes) and stderr (bytes).
        """
        stdout_result = []
        stderr_result = []
        with subprocess.Popen(command,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True,
                                shell=True) as proc:
            stdout_thread = threading.Thread(target=_read_stream,
                                             args=(proc.stdout, 'stdout',stdout_result))
            stderr_thread = threading.Thread(target=_read_stream,
                                             args=(proc.stderr, 'stderr', stderr_result))
            stdout_thread.start()
            stderr_thread.start()
            # Wait for the process to finish
            return_code = proc.wait()
            # Ensure threads finish reading and collect data
            stdout_thread.join()
            stdout = stdout_result[0]
            stderr_thread.join()
            stderr = stderr_result[0]
        return stdout, stderr, return_code

    def _run_commands(self, commands: list[str]) -> tuple[list[str],list[str],list[int]]:
        """
        Runs a list of commands in the self.commands attribute and returns the stdout, stderr, and exit
        codes for each command.

        Returns:
            Returns a tuple containing three lists: `stdout_list`, `stderr_list`, and `exit_code_list`.
              Each list contains the respective outputs (stdout, stderr,
              and exit code) of running the command(s) specified in the `self.commands` attribute.
        """
        stdout_list = []
        stderr_list = []
        exit_code_list = []
        for command in commands:
            stdout, stderr, exit_code = self._run_command(command)
            stdout_list.append(stdout)
            stderr_list.append(stderr)
            exit_code_list.append(exit_code)
            if self._fail_fast and exit_code_list[-1] > 0:
                break
        return stdout_list, stderr_list, exit_code_list


    def run(self, args: list[str], config:dict|io.IOBase|str=None) -> tuple:
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
        commands = self._engine.get_commands(args)
        return self._run_commands(commands)

def _read_stream(stream:io.IOBase, target:str, result_list:list):
    """Read data from a stream and writes it to either stdout or stderr whilst also
    capturing the data.

    Args:
        stream (io.IOBase): Stream object from which data will be read.
        target (str): Where the output from the stream should be directed. Either 'stdout' or 'stderr'
        result_list (list): The list that will store the data read from the stream.
            Each chunk of data read from the stream will be appended to this list.
    """
    data = ''
    if target == 'stdout':
        output = sys.stdout
    elif target == 'stderr':
        output = sys.stderr

    while True:
        chunk = stream.readline()
        if chunk == '':
            break
        data += chunk
        output.write(chunk)
        output.flush()
    result_list.append(data)
