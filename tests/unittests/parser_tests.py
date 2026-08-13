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
"""Test both Parser and ParserBuilder together."""
import argparse
from contextlib import redirect_stdout
import io
import unittest

from yaml_runner.exceptions import InvalidCommandError
from yaml_runner.models import ArgumentNode, CommandNode, FlagNode, OptionNode
from yaml_runner.parser import ParserBuilder

class ParserTests(unittest.TestCase):
    """Tests Parser and ParserBuilder together due to their linked nature."""
    def setUp(self):
        self.builder = ParserBuilder(argparse.ArgumentParser, "program")

    def test_command_sets_command(self):
        commands = {
            "run": CommandNode(command=["echo"])
        }

        parser = self.builder.build(commands)
        result = parser.parse(["run"])

        self.assertEqual(result.commands, ["echo"])

    def test_command_help_message(self):
        commands = {
            "run": CommandNode(command=["echo"], description="Help message")
        }
        output = io.StringIO()

        parser = self.builder.build(commands)
        with redirect_stdout(output):
            with self.assertRaises(SystemExit) as context:
                parser.parse(["run", "--help"])

        self.assertEqual(context.exception.code, 0)
        self.assertIn("Help message", output.getvalue())

    def test_unknown_command_errors(self):
        commands = {
            "run": CommandNode(command=["echo"])
        }

        parser = self.builder.build(commands)

        with self.assertRaises(InvalidCommandError) as context:
            parser.parse(["nope"])

        self.assertIn("invalid choice: 'nope' (choose from run)", str(context.exception))

    def test_positional_arguments(self):
        commands = {
            "run": CommandNode(
                command = ["echo"],
                arguments = {
                    "mode": ArgumentNode()
                }
            )
        }

        parser = self.builder.build(commands)
        result = parser.parse(["run", "a"])

        self.assertEqual(result.params["mode"], "a")

    def test_missing_positional_argument_errors(self):
        commands = {
            "run": CommandNode(
                command = ["echo"],
                arguments = {
                    "mode": ArgumentNode()
                }
            )
        }

        parser = self.builder.build(commands)

        with self.assertRaises(InvalidCommandError):
            parser.parse(["run"])

    def test_positional_arguments_errors_on_invalid_choice(self):
        commands = {
            "run": CommandNode(
                command = ["echo"],
                arguments = {
                    "mode": ArgumentNode(choices=["a", "b"])
                }
            )
        }

        parser = self.builder.build(commands)
        with self.assertRaises(InvalidCommandError) as context:
            parser.parse(["run", "c"])

        self.assertIn("argument mode: invalid choice: 'c'", str(context.exception))

    def test_positional_arguments_help_message(self):
        commands = {
            "run": CommandNode(
                command = ["echo"],
                arguments = {
                    "mode": ArgumentNode(choices=["a", "b"], description="Arg help")
                }
            )
        }
        output = io.StringIO()

        parser = self.builder.build(commands)
        with redirect_stdout(output):
            with self.assertRaises(SystemExit) as context:
                parser.parse(["run", "--help"])

        self.assertEqual(context.exception.code, 0)
        self.assertIn("Arg help", output.getvalue())

    def test_option_long_and_short(self):
        commands = {
            "run": CommandNode(
                command = ["echo"],
                options = {
                    "output": OptionNode(short="o")
                }
            )
        }

        parser = self.builder.build(commands)
        result = parser.parse(["run", "--output", "file"])
        self.assertEqual(result.params["output"], "file")

        result = parser.parse(["run", "-o", "file"])
        self.assertEqual(result.params["output"], "file")

    def test_option_required_enforced(self):
        commands = {
            "run": CommandNode(
                command = ["echo"],
                options = {
                    "output": OptionNode(short="o", required=True)
                }
            )
        }

        parser = self.builder.build(commands)

        with self.assertRaises(InvalidCommandError) as context:
            parser.parse(["run"])

        self.assertIn("the following arguments are required", str(context.exception))

    def test_option_description_in_help_message(self):
        commands = {
            "run": CommandNode(
                command = ["echo"],
                options = {
                    "output": OptionNode(description="Option help")
                }
            )
        }

        output = io.StringIO()

        parser = self.builder.build(commands)
        with redirect_stdout(output):
            with self.assertRaises(SystemExit) as context:
                parser.parse(["run", "--help"])

        self.assertEqual(context.exception.code, 0)
        self.assertIn("Option help", output.getvalue())

    def test_flag_long_and_short(self):
        commands = {
            "run": CommandNode(
                command = ["echo"],
                flags = {
                    "aflag": FlagNode(value="avalue", short="a")
                }
            )
        }

        parser = self.builder.build(commands)

        result = parser.parse(["run", "--aflag"])
        self.assertEqual(result.params["aflag"], "avalue")

        result = parser.parse(["run", "-a"])
        self.assertEqual(result.params["aflag"], "avalue")

    def test_flag_description_in_help_message(self):
        commands = {
            "run": CommandNode(
                command = ["echo"],
                flags = {
                    "aflag": FlagNode(value="avalue", description="Flag help")
                }
            )
        }

        output = io.StringIO()

        parser = self.builder.build(commands)
        with redirect_stdout(output):
            with self.assertRaises(SystemExit) as context:
                parser.parse(["run", "--help"])

        self.assertEqual(context.exception.code, 0)
        self.assertIn("Flag help", output.getvalue())

    def test_groups_descend_flags_and_options_to_lower_commands(self):
        commands = {
            "run": CommandNode(
                flags = {
                    "aflag": FlagNode(value="f_value")
                },
                options = {
                    "anoption": OptionNode()
                },
                subcommands = {
                    "asubcommand": CommandNode(
                        command = ["echo"]
                    )
                }
            )
        }

        parser = self.builder.build(commands)
        result = parser.parse(["run", "asubcommand", "--aflag", "--anoption", "op_value"])

        self.assertEqual(result.params["aflag"], "f_value")
        self.assertEqual(result.params["anoption"], "op_value")

    def test_passthrough_on_allowed_commands(self):
        commands = {
            "run": CommandNode(
                command = ["echo"],
                passthrough = True
            )
        }

        parser = self.builder.build(commands)
        result = parser.parse(["run", "pass", "through"])

        self.assertEqual(result.passthrough, ["pass", "through"])

    def test_error_on_passthrough_when_not_enabled(self):
        commands = {
            "run": CommandNode(
                command = ["echo"]
            )
        }

        parser = self.builder.build(commands)

        with self.assertRaises(InvalidCommandError):
            parser.parse(["run", "pass", "through"])

    def test_options_and_flags_can_come_after_passthrough(self):
        commands = {
            "run": CommandNode(
                command = ["echo"],
                passthrough = True,
                flags = {
                    "aflag": FlagNode(value="fvalue")
                },
                options = {
                    "anoption": OptionNode()
                }
            )
        }

        parser = self.builder.build(commands)
        result = parser.parse(["run", "pass", "through", "--aflag", "--anoption", "ovalue"])

        self.assertEqual(result.passthrough, ["pass", "through"])
        self.assertEqual(result.params["aflag"], "fvalue")
        self.assertEqual(result.params["anoption"], "ovalue")


    def test_sibling_doesnt_take_flags_or_options(self):
        commands = {
            "group": CommandNode(
                subcommands = {
                    "foo": CommandNode(
                        command = ["echo"],
                        flags = {"aflag": FlagNode(value="avalue")},
                        options = {"anoption": OptionNode()}
                    ),
                    "bar": CommandNode(
                        command = ["echo"]
                    )
                }
            )
        }

        parser = self.builder.build(commands)

        with self.assertRaises(InvalidCommandError):
            parser.parse(["group", "bar", "--aflag"])

        with self.assertRaises(InvalidCommandError):
            parser.parse(["group", "bar", "--anoption"])

    def test_nested_command_doesnt_take_parents_command(self):
        commands = {
            "group": CommandNode(
                command=["parent"],
                subcommands={
                    "child": CommandNode(command=["child"])
                }
            )
        }

        parser = self.builder.build(commands)
        result = parser.parse(["group", "child"])

        self.assertEqual(result.commands, ["child"])

if __name__ == "__main__":
    unittest.main()
