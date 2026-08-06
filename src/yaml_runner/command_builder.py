"""Render parsed commands by substituing placeholders with values.

Takes command templates (e.g. "echo {{name}}") and replaces placeholders
with the corresponding values to produce executable command strings.
"""
import re

from .parser import ParsedCommand

def build(parsed_command: ParsedCommand) -> list[str]:
    """Render command templates into concrete command strings by replacing
    {{key}} in command templates with values in parsed_command.params.

    Example:
        parsed_command.command = ["echo {{name}} $@"]
        parsed_command.params = {"name": "Benji"}
        parsed_command.passthrough = ["!"]

        Returns ["echo Benji !"]
    """
    commands = []
    for command in parsed_command.commands:
        commands.append(_render(command, parsed_command))
    return commands

def _render(command_template: str, parsed_command: ParsedCommand):
    """Replace {{key}} in template with values from params and $@ with any extra passthrough args."""
    command_template = command_template.replace("$@", " ".join(parsed_command.passthrough))
    return re.sub(
        r"\{\{(\w+)\}\}",
        lambda m: parsed_command.params[m.group(1)] if m.group(1) in parsed_command.params else "",
        command_template
    )
