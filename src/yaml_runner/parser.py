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

from .models import ArgumentNode, CommandNode, FlagNode, OptionNode, ParsedCommand
from .exceptions import InvalidCommandError

class Parser:
    def __init__(self, parser: argparse.ArgumentParser):
        self._parser = parser

    def parse(self, args: list[str]) -> ParsedCommand:
        namespace, remainder = self._parser.parse_known_args(args)
        if namespace.command is None:
            raise InvalidCommandError(f"Unknown command passed: {' '.join(args)}")

        data = vars(namespace).copy()
        commands = data.pop("command")
        passthrough = data.pop("passthrough", [])

        if remainder and data.pop("passthrough_allowed") == False:
            raise InvalidCommandError(
                f"Extra args passed '{remainder}' and passthrough not enabled.")

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
        parser = self.parser_cls(prog=self.program)
        subparser = parser.add_subparsers()
        self._build_recursive(command_nodes=command_nodes, subparser=subparser)
        return Parser(parser)

    def _build_recursive(
        self,
        subparser: argparse._SubParsersAction,
        command_nodes: dict[str, CommandNode]
    ):
        """Recursively build parser for commands and nested subcommands."""
        for name, command_node in command_nodes.items():
            cmd_parser = subparser.add_parser(name)
            if command_node.command:
                self._add_command(cmd_parser, command_node)
            if command_node.subcommands:
                cmd_subparser = cmd_parser.add_subparsers()
                self._build_recursive(cmd_subparser, command_node.subcommands)

    def _add_command(
        self,
        cmd_parser: argparse.ArgumentParser,
        command_node: CommandNode
    ):
        """Attach command behavior and arguments to a parser."""
        # Metadata
        cmd_parser.set_defaults(
            command=command_node.command, passthrough_allowed=command_node.passthrough)

        # Additional args/options
        self._add_arguments(cmd_parser, command_node.arguments, command_node.passthrough)
        self._add_options(cmd_parser, command_node.options)
        self._add_flags(cmd_parser, command_node.flags)

    def _add_arguments(
        self,
        cmd_parser: argparse.ArgumentParser,
        arguments: dict[str, ArgumentNode],
        passthrough: bool
    ):
        for name, argument in arguments.items():
            cmd_parser.add_argument(
                name,
                choices=argument.choices,
                help=argument.description
            )
        if passthrough:
            cmd_parser.add_argument(
                'passthrough',
                action='store',
                help='Extra arguments for the command.',
                nargs=argparse.REMAINDER,
            )

    def _add_options(
            self, cmd_parser: argparse.ArgumentParser, options: dict[str, OptionNode]):
        """Add options to a parser."""
        for name, option in options.items():
            names = [f"--{name}"]
            if option.short:
                names.append(f"-{option.short}")

            cmd_parser.add_argument(
                *names,
                help=option.description,
                required=option.required
            )

    def _add_flags(self, cmd_parser: argparse.ArgumentParser, flags: dict[str, FlagNode]):
        """Add flags to a parser."""
        for name, flag in flags.items():
            names = [f"--{name}"]
            if flag.short:
                names.append(f"-{flag.short}")

            cmd_parser.add_argument(
                *names,
                help=flag.description,
                action='store_const',
                const=flag.value
            )
