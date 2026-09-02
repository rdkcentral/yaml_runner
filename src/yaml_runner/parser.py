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
import os

from argparse_completion import argparse_completion

from .models import ArgumentNode, CommandNode, ParsedCommand
from .exceptions import InvalidCommandError

class Parser:
    """Parses command-line arguments using a parser built by ParserBuilder.

    ParserBuilder adds metadata to each command parser that identifies the command
    to run and whether extra arguments can be passed through. Parser uses this
    metadata when turning the provided arguments into a ParsedCommand.
    """
    def __init__(self, parser: argparse.ArgumentParser):
        self._parser = parser

    def parse(self, args: list[str]) -> ParsedCommand:
        """Parse the provided arguments and return the command to run.

        Uses metadata added by ParserBuilder to determine the command and whether
        any extra arguments are allowed.

        Raises InvalidCommandError if no command is found or unexpected extra
        arguments are provided.
        """
        try:
            namespace, passthrough = self._parser.parse_known_args(args)
        except argparse.ArgumentError as e:
            raise InvalidCommandError(f"{e}") from e

        data = vars(namespace).copy()
        try:
            commands = data.pop("command")
        except KeyError:
            raise InvalidCommandError(
                "Provided args don't correspond to any known command.")
        passthrough_allowed = data.pop("passthrough_allowed")

        if passthrough and not passthrough_allowed:
            raise InvalidCommandError(
                f"Unknown arguments passed in '{passthrough}'.")

        return ParsedCommand(
            commands=commands,
            params=data,
            passthrough=passthrough
        )

    def get_completion(self, completion_shell: str):
        os.environ['_ARGPARSE_COMPLETE'] = completion_shell
        return argparse_completion.get_completion(self._parser)

class ParserBuilder:
    """Constructs an argparse-based parser from a command tree."""
    def __init__(
        self,
        parser_cls: type[argparse.ArgumentParser],
        program: str,
    ):
        self.parser_cls = parser_cls
        self.program = program

    def build(
        self,
        command_nodes: dict[str, CommandNode]
    ) -> Parser:
        """Build and return a parser configured from command definitions."""
        parser = self.parser_cls(prog=self.program, exit_on_error=False)
        subparser = parser.add_subparsers(required=True)
        self._build_recursive(command_nodes=command_nodes, subparser=subparser)
        return Parser(parser)

    def _build_recursive(
        self,
        subparser: argparse._SubParsersAction,
        command_nodes: dict[str, CommandNode],
    ):
        """Recursively build parser for commands and nested subcommands."""
        for name, command_node in command_nodes.items():
            cmd_parser = subparser.add_parser(
                name,
                help=command_node.description,
                description=command_node.description,
                exit_on_error=False
            )

            if command_node.command:
                self._add_command(cmd_parser, command_node)
                self._add_arguments(cmd_parser, command_node.arguments)
                self._setup_passthrough(cmd_parser, command_node.passthrough)

            if command_node.subcommands:
                cmd_subparser = cmd_parser.add_subparsers()
                self._build_recursive(
                    cmd_subparser,
                    command_node.subcommands,
                )

    def _add_command(
        self,
        cmd_parser: argparse.ArgumentParser,
        command_node: CommandNode
    ):
        """Attach command behavior to a parser."""
        cmd_parser.set_defaults(command=command_node.command)

    def _add_arguments(
        self,
        cmd_parser: argparse.ArgumentParser,
        arguments: dict[str, ArgumentNode],
    ):
        for name, argument in arguments.items():
            cmd_parser.add_argument(
                name,
                choices=argument.choices,
                help=argument.description
            )

    def _setup_passthrough(
            self,
            cmd_parser: argparse.ArgumentParser,
            passthrough: bool
    ):
        """Setup passthrough behaviour for a parser.

        Adds metadata to tell Parser() to use argparses builtin remainder args.
        Adds a note to the end of the help message to tell the user passthrough is enabled.
        """
        cmd_parser.set_defaults(passthrough_allowed=passthrough)
        if passthrough:
            cmd_parser.epilog = (
               "PASSTHROUGH ENABLED: Any additional arguments are passed through to the "
               "underlying command."
            )
