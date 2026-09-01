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

from .base_config_reader import BaseConfigReader
from ..exceptions import ConfigValidationError
from ..models import CommandNode, COMMAND_SECTIONS

class HierarchicalConfigReader(BaseConfigReader):
    """Takes a hierarchical config in dictionary form and extracts into concrete models."""
    def get_commands(self) -> dict[str, CommandNode]:
        stripped_config = self._strip_config(self.config)

        commands: dict[str, CommandNode] = {}
        for key, value in stripped_config.items():
            commands[key] = self._build_command_node(value, f"{key}.")
        return commands

    def _strip_config(self, config: dict) -> dict:
        """
        Recursively strip the dict down to trees that contain commands.

        Args:
            config (dict): Dictionary containing command configuration data.

        Returns:
            dict: Config dictionary containing only sections with commands.
        """
        result = {}

        for key, value in config.items():
            if not isinstance(value, dict):
                continue

            child = self._strip_config(value)

            if "command" in value:
                result[key] = {
                    section: section_value
                    for section, section_value in value.items()
                    if section in COMMAND_SECTIONS
                }
                result[key].update(child)

            elif child:
                result[key] = {
                    section: section_value
                    for section, section_value in value.items()
                    if section in COMMAND_SECTIONS
                }

                result[key].update(child)

        return result

    def _build_command_node(self, data: dict, path: str) -> CommandNode:
        """Build a command node and recursively build all subcommands.

        Raises ConfigValidationError if the command node or any subcommands are
        invalid.
        """
        subcommands = self._extract_subcommands(data, path)

        try:
            return self._create_command_node(data, subcommands)
        except ConfigValidationError as e:
            raise ConfigValidationError(f"Error at path '{path}': {e}") from e

    def _extract_subcommands(self, data: dict, path: str) -> dict[str, CommandNode]:
        """Extract any key not in the known command sections as a subcommand.

        Returns a dictionary of subcommands and their CommandNode.

        Raises ConfigValidationError if any key not in the known command sections
        isn't a valid subcommand.
        """
        subcommands = {}
        for key, value in data.items():
            if key in COMMAND_SECTIONS:
                continue

            subcommands[key] = self._build_command_node(value, path + key + ".")
        return subcommands
