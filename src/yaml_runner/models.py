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

from dataclasses import dataclass, field

from pydantic import BaseModel, Field, model_validator

# Fields a command can contain.
COMMAND_SECTIONS = frozenset(
    {"description", "command", "args", "params"})

class ArgumentNode(BaseModel):
    """Represents arguments for a command."""
    choices: list[str] | None = None
    description: str | None = None

class CommandNode(BaseModel):
    """Represents a node describing a command or a group.

    If a CommandNode.command == None it's describing a group (a container for subcommands).
    If CommandNode.command == list[str] it's describing a command, which can also contain
    subcommands.

    Groups can still contain options or flags which all subcommands can use but cannot
    contain positional arguments.
    """
    description: str | None = None
    command: list[str] | None = None
    arguments: dict[str, ArgumentNode] = Field(default_factory=dict)
    passthrough: bool = False
    subcommands: dict[str, "CommandNode"] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_model(self) -> "CommandNode":
        if not self.command and not self.subcommands:
            raise ValueError("Must either define a command or contain a subcommand.")

        if self.subcommands and self.arguments:
            raise ValueError(
                "Nodes with subcommands cannot define positional arguments.")
        return self

@dataclass
class ParsedCommand:
    """A list of commands and passed in parameters."""
    commands: list[str]
    params: dict[str, str] = field(default_factory=dict)
    passthrough: list[str] = field(default_factory=list)

# order=True means we can sort CompletedCommands numerically by their exit_code
@dataclass(order=True)
class CompletedCommand:
    """Information about a completed command."""
    exit_code: int
    stdout: str
    stderr: str
