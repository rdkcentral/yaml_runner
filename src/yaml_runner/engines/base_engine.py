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

from abc import ABC,abstractmethod
import argparse

class BaseYamlRunnerEngine(ABC):

    def __init__(self, config, program: str=''):
        self._config = {}
        if config:
            self.config = config
        self._arg_parser = argparse.ArgumentParser(prog=program)

    @property
    def config(self):
        """The config currently in use by the YamlRunner"""
        return self._config.copy()

    @config.setter
    def config(self,config: dict):
        if isinstance(config,dict):
            self._config = config
        else:
            raise TypeError('Expected config as type: dict')

    @abstractmethod
    def get_commands(self, args: list[str]) -> list[str]:
        """
        This method takes in the cli args as a list of strings.
        Setup the parsers. Parses the arguments to work out the commands to be run.
        Returns the commands to be run as a list of strings.

        Returns:
            list[str]: List of strings, commands to be run.
        """
        pass

    @abstractmethod
    def _process_arguments(self, args: list[str]) -> dict:
        """
        Sets up and runs argument parser/s for each command section
        found in the config. Returning the namespace object from the parsed
        arguments as a dictionary.

        Args:
            args (list[str]): Unparsed arguments in a list.

        Returns:
            dict: Dictionary of arguments and their values.
        """
        pass

    def _get_command_sections(self, parsed_config: dict) -> list[str]:
        """
        Recursive function to extract the command sections from a dictionary.
        
        Args:
        parsed_config (dict): Dictionary containing command configiguration data.
        
        Returns:
        A list of dictionaries containing command sections from the parsed configuration. Each
        dictionary includes the 'name' key with the corresponding key from the parsed configuration.
        """
        command_dicts = []
        for key, value in parsed_config.items():
            if isinstance(value,dict):
                if value.get('command',None):
                    value.update({'name':key})
                    command_dicts.append(value)
                else:
                    command_dicts += self._get_command_sections(value)
        return command_dicts

    def _add_params_parser(self,parser: argparse.ArgumentParser, params:dict):
        """Add command parameters to the commands parser.
        Takes in the commands "params" section from the config and the commands subparser.

        Args:
            parser (argparse.ArgumentParser): Commands subparser.
            params (dict): Params section from yaml config.
        """
        if params.get('passthrough'):
            parser.add_argument('passthrough',
                                action='store',
                                help='Extra arguments for the command.',
                                nargs=argparse.REMAINDER,
                                metavar='ARGUMENTS')

    def _build_commands(self, commands:list[str], cli_args: dict) -> list[str]:
        """_summary_

        Args:
            commands (list[str]): _description_
            cli_args (dict): _description_

        Returns:
            list[str]: _description_
        """
        if 'passthrough' in cli_args.keys():
            for index,command in enumerate(commands):
                cli_arg_string = ' '.join(cli_args.get('passthrough',[]))
                commands[index] = command.replace('$@',cli_arg_string)
        return commands

    def get_commands(self, cli_args: list[str]) -> list[str]:
        parsed_args =  self._process_arguments(cli_args)
        if parsed_args.get('command_name'):
            command_dict = list(filter(lambda x: x.get('name') == parsed_args.get('command_name'),
                                       self._get_command_sections(self._config)))[0]
            command_strings = command_dict.get('command')
            if isinstance(command_strings,str):
                command_strings = [command_strings]
            return self._build_commands(command_strings,parsed_args)
        else:
            raise RuntimeError('No command was given, although it was required')