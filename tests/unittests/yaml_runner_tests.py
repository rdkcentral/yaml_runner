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
import io
import unittest
from unittest.mock import patch

from yaml_runner.yaml_runner import YamlRunner
from yaml_runner.exceptions import ConfigLoadError, InvalidCommandError

SIMPLE_CONFIG = {
    "run": {
        "hello_world": {
            "command": 'echo "hello world"',
            "description": "Print hello world in stdout.",
        },
        "echo_passthrough": {
            "command": "echo $@",
            "params": {
                "passthrough": True,
            },
        },
    },
}

HIERARCHICAL_CONFIG = {
    "run": {
        "argument_command": {
            "command": "echo {{anargument}}",
            "args": {
                "anargument": {
                    "choices": ["a", "b"],
                }
            },
        },
    }
}

class TestYamlRunner(unittest.TestCase):
    def test_invalid_config_type_raises_config_load_error(self):
        with self.assertRaises(ConfigLoadError):
            YamlRunner(object())

    def test_missing_config_file_raises_config_load_error(self):
        with self.assertRaises(ConfigLoadError):
            YamlRunner("/does/not/exist.yaml")

    def test_invalid_yaml_raises_config_load_error(self):
        config = io.StringIO("""
        foo:
          bar:
            - invalid
           indentation
        """)

        with self.assertRaises(ConfigLoadError):
            YamlRunner(config)

    @patch("yaml_runner.yaml_runner.command_runner.run_commands")
    def test_run_builds_command_from_config(self, run_commands):
        run_commands.return_value = []

        runner = YamlRunner(SIMPLE_CONFIG)
        runner.run(["hello_world"])

        commands, fail_fast = run_commands.call_args.args

        self.assertEqual(len(commands), 1)
        self.assertEqual(commands[0], 'echo "hello world"')
        self.assertTrue(fail_fast)

    @patch("yaml_runner.yaml_runner.command_runner.run_commands")
    def test_passthrough_arguments_are_added_to_command(self, run_commands):
        run_commands.return_value = []

        runner = YamlRunner(SIMPLE_CONFIG)
        runner.run(["echo_passthrough", "foo", "bar"])

        commands, _ = run_commands.call_args.args

        self.assertEqual(commands, ["echo foo bar"])

    @patch("yaml_runner.yaml_runner.command_runner.run_commands")
    def test_setting_config_changes_available_commands(self, run_commands):
        run_commands.return_value = []

        runner = YamlRunner({
            "run": {
                "old": {
                    "command": "echo old",
                }
            }
        })

        runner.config = {
            "run": {
                "new": {
                    "command": "echo new",
                }
            }
        }

        runner.run(["new"])

        commands, _ = run_commands.call_args.args

        self.assertEqual(commands, ["echo new"])

    @patch("yaml_runner.yaml_runner.command_runner.run_commands")
    def test_fail_fast_is_forwarded(self, run_commands):
        run_commands.return_value = []

        runner = YamlRunner(SIMPLE_CONFIG, fail_fast=False)
        runner.run(["hello_world"])

        _, fail_fast = run_commands.call_args.args

        self.assertFalse(fail_fast)

    @patch("yaml_runner.yaml_runner.command_runner.run_commands")
    def test_hierarchical_argument(self, run_commands):
        run_commands.return_value = []

        runner = YamlRunner(HIERARCHICAL_CONFIG, hierarchical=True)
        runner.run([
            "run",
            "argument_command",
            "a",
        ])

        commands, _ = run_commands.call_args.args

        self.assertEqual(commands, ["echo a"])

    def test_hierarchical_invalid_argument_choice_raises_invalid_command(self):
        runner = YamlRunner(HIERARCHICAL_CONFIG, hierarchical=True)

        with self.assertRaises(InvalidCommandError):
            runner.run([
                "run",
                "argument_command",
                "c",
            ])

if __name__ == "__main__":
    unittest.main()
