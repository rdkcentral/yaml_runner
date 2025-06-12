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
import re
from os import path
import unittest

MY_PATH = path.abspath(__file__)
MY_DIR = path.dirname(MY_PATH)

class CLITest(unittest.TestCase):
    """Test class for the yaml_runner script."""
    yaml_runner_script = path.join(MY_DIR, '../src/yaml_runner/cli.py')

    def _help_to_dict(cls,help_output: str) -> dict:
        """
        Convert the a help message into a dictionary of usage,
        optional argumens and positional arguments.

        Args:
            help_output (str): The full string of the commands help message.

        Returns:
            dict: {usage:string, options: list[dict], postionals: list[dict]} 
        """
        help_output_lines = help_output.splitlines()
        result_dict = {}
        usage = []
        usage_bool = False
        options_bool = False
        options = []
        positionals_bool = False
        positionals = []
        for index,line in enumerate(help_output_lines):
            if line == '':
                continue
            elif 'usage:' in line:
                usage_bool = True
                options_bool = False
                positionals_bool = False
                usage.append(line)
            elif 'options:' in line:
                options_bool = True
                positionals_bool = False
                usage_bool = False
            elif 'positional arguments:' in line:
                positionals_bool = True
                options_bool = False
                usage_bool = False
            elif usage_bool:
                usage.append(line)
            elif options_bool:
                options.append(line)
            elif positionals_bool:
                positionals.append(line)
            else:
                options_bool = False
                positionals_bool = False
                usage_bool = False
        result_dict.update(_process_usage(usage))
        result_dict.update(_process_options(options))
        result_dict.update(_process_positionals(positionals))
        return result_dict

def _process_usage(usage_lines:list[str]) -> dict:
    """
    Processes the usage lines from the help output.

    Args:
        usage_lines (list[str]): Usage lines from the help output.

    Returns:
        dict: Dictionary with the key "usage" and value set to the usage text.
    """
    first_line = usage_lines.pop(0)
    usage_string = first_line.split(':')[-1]
    if len(usage_lines) > 0:
        for line in usage_lines:
            usage_string += ' ' + line.strip()
    return {'usage': usage_string}

def _process_options(option_lines:list[str]) -> dict:
    """
    Process the options lines from the help output.

    Args:
        option_lines (list[str]): Options lines from help output.

    Returns:
        dict: Dictionary with the key "options". Value as a secondary dictionary
              with the keys set to the options listed in the help output, and their
              values being their descriptions.
    """
    options_list = {}
    for index,line in enumerate(option_lines):
        if line.strip().startswith('-'):
            options_regex = re.search(r'(-+.+?(?=[,| ]))\s{2,}(.*)$',line)
            if options_regex:
                option_strings = options_regex.group(1).split(',')
                option_desc = options_regex.group(2)
            else:
                option_strings = line.strip().split(',')
                option_desc = ''
        else:
                if option_desc == '':
                    option_desc += line.strip()
                else:
                    option_desc += ' ' + line.strip()
        if (index == len(option_lines)-1) or option_lines[index+1].startswith('-'):
            for option in option_strings:
                options_list.update({option.strip():option_desc})
    return {'options':options_list}

def _process_positionals(positional_lines: list[str]) -> dict:
    """
    Processes positional lines from the help output.

    Args:
        positional_lines (list[str]): Positional lines from the help output.

    Returns:
        dict: Dictionary with the key "positionals". Value as a secondary
              dictionary with the keys as the positionals name and values as their
              descriptions.
    """
    positonal_list = {}
    for index,line in enumerate(positional_lines):
        if line.strip().startswith('{'):
            continue
        if positional_regex := re.search(r'([\S]+)\s{2,}([\S| ]+)$',line.strip()):
            positional_arg = positional_regex.group(1)
            positional_desc = positional_regex.group(2)
        else:
            positional_desc += ' ' + line.strip()
        if ((index == len(positional_lines)-1) or 
                re.search(r'([\S]+)\s{2,}([\S| ]+)$',positional_lines[index+1].strip())):
            positonal_list.update({positional_arg:positional_desc})
    return {'positionals': positonal_list}