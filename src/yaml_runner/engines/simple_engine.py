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

from .base_engine import BaseYamlRunnerEngine
from ..exceptions import ConfigValidationError
from ..models import CommandNode

class SimpleEngine(BaseYamlRunnerEngine):
    """YamlRunner class for executing commands from a YAML configuration file.

    This class provides a framework for running commands defined within a YAML
    configuration file. It allows for parsing arguments from the command line,
    processing the YAML configuration, and executing the defined commands.

    Attributes:
        _arg_parser (argparse.ArgumentParser): The main argument parser for the script.
    """

    def _setup_commands(self):
        if self._commands:
            self._commands = {}
        self._get_command_sections(self._config)

    def _get_command_sections(self, parsed_config: dict):
        """
        Recursive function to extract the command sections from a dictionary.

        Args:
        parsed_config (dict): Dictionary containing command configuration data.

        Returns:
        A list of dictionaries containing command sections from the parsed configuration. Each
        dictionary includes the 'name' key with the corresponding key from the parsed configuration.
        """
        for key, value in parsed_config.items():
            if isinstance(value, dict):
                if value.get('command'):
                    if key in self._commands:
                        raise ConfigValidationError(
                            f"Two commands in config with {key}. "
                            "Maybe you meant to use hierarchical mode?")

                    try:
                        node = self._create_command_node(value)
                    except ConfigValidationError as e:
                        raise ConfigValidationError(
                            f"Config error with command {key}: {str(e)}") from e
                    self._commands[key] = node
                else:
                    self._get_command_sections(value)
