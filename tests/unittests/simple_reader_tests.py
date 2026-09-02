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

from yaml_runner.config_readers.simple_config_reader import SimpleConfigReader
from yaml_runner.exceptions import ConfigValidationError

class SimpleConfigReaderTest(unittest.TestCase):
    def test_get_commands_returns_flat_commands(self):
        config = {
            "hello": {
                "command": "echo hello",
                "description": "Say hello"
            },
            "goodbye": {
                "command": "echo goodbye"
            }
        }

        commands = SimpleConfigReader(config).get_commands()

        self.assertEqual(set(commands), {"hello", "goodbye"})
        self.assertEqual(commands["hello"].command, ["echo hello"])
        self.assertEqual(commands["hello"].description, "Say hello")
        self.assertEqual(commands["goodbye"].command, ["echo goodbye"])

    def test_get_commands_returns_nested_commands(self):
        config = {
            "something": {
                "deep": {
                    "hello": {
                        "command": "echo hello"
                    }
                }
            }
        }

        commands = SimpleConfigReader(config).get_commands()

        self.assertIn("hello", commands)

    def test_duplicate_command_names_raise(self):
        config = {
            "group_a": {
                "hello": {"command": "echo one"},
            },
            "group_b": {
                "hello": {"command": "echo two"},
            },
        }

        with self.assertRaises(ConfigValidationError):
            SimpleConfigReader(config).get_commands()

    def test_correctly_reads_multiple_commands(self):
        config = {
            "hello": {
                "command": ["echo one", "echo two"]
            }
        }

        commands = SimpleConfigReader(config).get_commands()

        self.assertEqual(commands["hello"].command, ["echo one", "echo two"])

if __name__ == "__main__":
    unittest.main()
