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
import unittest

from yaml_runner import command_builder
from yaml_runner.models import ParsedCommand

class TestCommandBuilder(unittest.TestCase):
    """Test rendering ParsedCommands into concrete commands to be ran."""
    def test_basic_replacement(self):
        parsed = ParsedCommand(
            commands=["echo {{name}}"],
            params={"name": "Alice"}
        )

        result = command_builder.build_commands(parsed)

        self.assertEqual(result, ["echo Alice"])

    def test_multiple_placeholders(self):
        parsed = ParsedCommand(
            commands=["{{greet}} {{name}}"],
            params={"greet": "Hello", "name": "Bob"}
        )

        result = command_builder.build_commands(parsed)

        self.assertEqual(result, ["Hello Bob"])

    def test_missing_key_replaced_with_empty(self):
        parsed = ParsedCommand(
            commands=["echo {{name}} {{missing}}"],
            params={"name": "Alice"}
        )

        result = command_builder.build_commands(parsed)

        self.assertEqual(result, ["echo Alice "])

    def test_repeated_placeholders(self):
        parsed = ParsedCommand(
            commands=["{{word}} {{word}}"],
            params={"word": "hi"}
        )

        result = command_builder.build_commands(parsed)

        self.assertEqual(result, ["hi hi"])

    def test_no_placeholders(self):
        parsed = ParsedCommand(
            commands=["ls -la"],
            params={"irrelevant": "value"}
        )

        result = command_builder.build_commands(parsed)

        self.assertEqual(result, ["ls -la"])

    def test_multiple_commands(self):
        parsed = ParsedCommand(
            commands = ["echo {{name}}", "cd {{dir}}"],
            params={"name": "Alice", "dir": "/tmp"}
        )

        result = command_builder.build_commands(parsed)

        self.assertEqual(result, ["echo Alice", "cd /tmp"])

    def test_passthrough(self):
        parsed = ParsedCommand(
            commands = ["echo $@"],
            passthrough = ["pass", "through"]
        )

        result = command_builder.build_commands(parsed)

        self.assertEqual(result, ["echo pass through"])

    def test_repeated_passthrough_replacements(self):
        parsed = ParsedCommand(
            commands = ["echo $@ $@", "echo again $@"],
            passthrough = ["pass", "through"]
        )

        result = command_builder.build_commands(parsed)

        self.assertEqual(result, ["echo pass through pass through", "echo again pass through"])

    def test_empty_passthrough_removes_placeholder(self):
        parsed = ParsedCommand(
            commands = ["echo $@"]
        )

        result = command_builder.build_commands(parsed)

        self.assertEqual(result, ["echo "])

    def test_params_and_passthrough_together(self):
        parsed = ParsedCommand(
            commands=["echo {{name}} $@"],
            params={"name": "Alice"},
            passthrough=["one", "two"],
        )

        result = command_builder.build_commands(parsed)

        self.assertEqual(result, ["echo Alice one two"])

if __name__ == "__main__":
    unittest.main()
