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

from abc import ABC, abstractmethod
import argparse

from pydantic import ValidationError

from .. import command_builder
from ..exceptions import ConfigValidationError
from ..models import CommandNode
from ..parser import ParserBuilder

class BaseYamlRunnerEngine(ABC):
    def __init__(
            self,
            config,
            parser_class: type[argparse.ArgumentParser] = argparse.ArgumentParser,
            program: str = ''):
        self._parser_builder = ParserBuilder(parser_class, program)
        self._commands: dict[str, CommandNode] = {}

        self.config = config

    @property
    def config(self):
        """The config currently in use by the YamlRunner"""
        return self._config.copy()

    @config.setter
    def config(self,config: dict):
        if isinstance(config,dict):
            self._config = config
            self._setup_commands()
            self._parser = self._parser_builder.build(self._commands)
        else:
            raise TypeError('Expected config as type: dict')

    def get_commands(self, cli_args: list[str]) -> list[str]:
        """
        This method takes in the cli args as a list of strings.
        Returns the commands to be run as a list of strings.

        Returns:
            list[str]: List of strings, commands to be run.
        """
        parsed_command = self._parser.parse(cli_args)
        return parsed_command.build()

    def get_completion(self, completion_shell: str):
        return self._parser.get_completion(completion_shell)

    @abstractmethod
    def _setup_commands(self):
        """
        Sets up the argument parser/s for each command section
        found in the config.
        """
        pass

    def _create_command_node(self, data: dict, subcommands: dict[str, CommandNode] = {}):
        def _normalize_command(command: str | list[str] | None) -> list[str] | None:
            if command is None:
                return None
            return [command] if isinstance(command, str) else command

        params = data.get("params", {})

        try:
            return CommandNode(
                description = data.get("description"),
                command = _normalize_command(data.get("command")),
                arguments = data.get("arguments") or {},
                options = data.get("options") or {},
                flags = data.get("flags") or {},
                passthrough = params.get("passthrough", False),
                subcommands = subcommands
            )
        except ValidationError as e:
            raise ConfigValidationError(f"{str(e)}") from e
