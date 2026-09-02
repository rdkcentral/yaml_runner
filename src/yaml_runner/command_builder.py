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
"""Takes a parsed command with metadata and builds it into a list of commands to run."""
import re

from .models import ParsedCommand

def build_commands(parsed: ParsedCommand) -> list[str]:
    """Render command templates into concrete command strings by replacing
    {{key}} in command templates with values in parsed_command.params.

    Example:
        parsed_command.command = ["echo {{name}} $@"]
        parsed_command.params = {"name": "Benji"}
        parsed_command.passthrough = ["!"]

        Returns ["echo Benji !"]
    """
    return [_render(command, parsed) for command in parsed.commands]

def _render(command_template: str, parsed: ParsedCommand):
    """Augment command string with passed values.

    Replace {{key}} in template with values from params and $@ with any extra
    passthrough args.
    """
    command_template = command_template.replace("$@", " ".join(parsed.passthrough))

    rendered = re.sub(
        r"\{\{(\w+)\}\}",
        lambda m: parsed.params.get(m.group(1), ""),
        command_template
    )
    return rendered
