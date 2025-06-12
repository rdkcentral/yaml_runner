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
"""CLITest unit tests for the yaml_runner script.

This module contains unit tests for `yaml_runner`.
The tests also rely on a sample configuration file
`examples/simple_config.yml`.

The tests verify the behavior of the script in the following scenarios:

* Running the script without arguments prints the help message and mentions
  the required `-c` or `--config` option for specifying the configuration file.
* Running the script with the `--help` option and a valid configuration file
  prints the script's usage information, including available choices and
  descriptions.
* Running the script with the `--config` option and a valid configuration file
  followed by a valid choice name (e.g., `hello_world`) executes the corresponding
  function and prints the expected output.
* Running the script with the `--config` option, a valid choice name supporting
  optional arguments (e.g., `echo_passthrough`), and the `--help` option prints the specific
  usage information for that choice.
* Running the script with `--config` 
"""


from os import path
import subprocess
import unittest

from cli_test_base import CLITest

MY_PATH = path.abspath(__file__)
MY_DIR = path.dirname(MY_PATH)

class SimpleCLITest(CLITest):
    """Test class for the yaml_runner script."""
    test_config_path = path.join(MY_DIR, '../examples/simple_config.yml')

    def test_1_no_config(self):
        """
        Tests that running the script without arguments prints the help message
        and mentions the required configuration file option.
        """
        result_no_args = subprocess.run(self.yaml_runner_script,
                                        text=True,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.STDOUT,
                                        check=False)
        result_help = subprocess.run([self.yaml_runner_script,
                                      '--help'],
                                        text=True,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.STDOUT,
                                        check=False)
        self.assertEqual(result_help.stdout,
                         result_no_args.stdout,
                         'Test both commands return the same results')
        help_dict = self._help_to_dict(result_help.stdout)
        self.assertIn('-c CONFIG',
                      help_dict.get('options',{}).keys(),
                      'Test the -c option is in the help output.')
        self.assertIn('--config CONFIG',
                      help_dict.get('options',{}).keys(),
                      'Test the --config option is in help outpu')
        self.assertIn('Yaml config to read from.', 
                      help_dict.get('options',{}).values(),
                      'Test the description for --config/-c is correct')

    def test_2_help_with_config(self):
        """
        Tests that running the script with --help and a valid configuration file
        prints the script's usage information.
        """
        result = subprocess.run([self.yaml_runner_script,
                                 '--config',
                                 self.test_config_path,
                                 '--help'],
                                text=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                check=False)
        self.assertEqual(result.returncode, 0, 'Test the exit code is zero')
        help_dict = self._help_to_dict(result.stdout)
        self.assertIn('hello_world',
                      help_dict.get('positionals',{}).keys(), 
                      'Test the hello_world choice is in the help message')
        self.assertIn('Print hello world in stdout.',
                      help_dict.get('positionals',{}).get('hello_world',''),
                      'Test the description of hello_world is in the help output')
        self.assertIn('echo_passthrough',
                      help_dict.get('positionals',{}).keys(),
                      'Test the echo_all choice is in the output')
        self.assertIn('Print all arguments passed after echo_passthrough.',
                      help_dict.get('positionals',{}).get('echo_passthrough',''),
                      'Test the description for echo_passthrough is in the help output')
        self.assertIn('list',
                      help_dict.get('positionals',{}).keys(),
                      'Test the echo_all choice is in the output')
        self.assertIn('Run each command listed in the command.',
                      help_dict.get('positionals',{}).get('list',''),
                      'Test the description for echo_passthrough is in the help output')
        self.assertIn('list_passthrough',
                      help_dict.get('positionals',{}).keys(),
                      'Test the echo_all choice is in the output')
        self.assertIn('Run each command listed, substituting the extra args in.',
                      help_dict.get('positionals',{}).get('list_passthrough',''),
                      'Test the description for echo_passthrough is in the help output')
        self.assertIn('-h',
                      help_dict.get('options',{}).keys(),
                      'Test the -h option is in the output')
        self.assertIn('--help',
                      help_dict.get('options',{}).keys(),
                      'Test the --help option is in the output')

    def test_3_hello_world(self):
        """
        Tests that running the script with a valid choice name executes
        the corresponding function and prints the expected output.
        """
        result = subprocess.run([self.yaml_runner_script,
                                 '--config',
                                 self.test_config_path,
                                 'hello_world'],
                                text=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                check=False)
        self.assertEqual(result.returncode, 0, 'Test the exit code is zero')
        self.assertEqual('hello world\n',result.stdout, 'Test "hello world" is printed in stdout')
        self.assertEqual(result.stderr, '', 'Test the stderr is empty')

    def test_4_passthrough_arg_in_help(self):
        """
        Tests that running the script with a choice supporting optional arguments
        and --help prints the specific usage information for that choice.
        """
        result = subprocess.run([self.yaml_runner_script,
                                 '--config',
                                 self.test_config_path,
                                 'echo_passthrough',
                                 '--help'],
                                text=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                check=False)
        self.assertEqual(result.returncode, 0, 'Test the exit code is zero')
        help_dict = self._help_to_dict(result.stdout)
        self.assertIn('echo_passthrough',
                      help_dict.get('usage',''),
                       'Test the echo_all choice is in the usage')
        self.assertIn('ARGUMENTS',
                      help_dict.get('positionals',{}).keys(),
                      'Test ARGUMENTS is shown as an optional argument.')
        self.assertIn('Extra arguments for the command.',
                      help_dict.get('positionals',{}).get('ARGUMENTS',''),
                      'Test the descriptions for passthough arguments is shown.')
        self.assertIn('-h',
                      help_dict.get('options',{}).keys(),
                      'Test the -h option is in the output')
        self.assertIn('--help',
                      help_dict.get('options',{}).keys(),
                      'Test the --help option is in the output')

    def test_5_passthrough_args(self):
        """Test passthough args work correctly
        """
        result = subprocess.run([self.yaml_runner_script,
                                 '--config',
                                 self.test_config_path,
                                 'echo_passthrough',
                                 'This',
                                 'is',
                                 'a',
                                 'test'],
                                text=True,
                                stdout=subprocess.PIPE,
                                check=False)
        self.assertEqual(result.returncode,
                         0,
                         'Test the exit code is zero')
        self.assertEqual('This is a test',
                         result.stdout.strip(),
                         'Test that args passed to passthrough are correctly passed through')

    def test_6_list_commands(self):
        """Test that list commands are run correctly
        """
        result = subprocess.run([self.yaml_runner_script,
                                 '--config',
                                 self.test_config_path,
                                 'list'],
                                text=True,
                                stdout=subprocess.PIPE,
                                check=False)
        self.assertEqual(result.returncode, 0, 'Test the exit code is zero')
        split_results = result.stdout.splitlines()
        self.assertEqual('echo 1',
                         split_results[0].strip(),
                         'Test the first command in the list ran first')
        self.assertEqual('echo 2',
                         split_results[1].strip(),
                         'Test the second command in the list ran second')
        self.assertEqual('echo 3',
                         split_results[2].strip(),
                         'Test the third command in the list ran third')
        self.assertEqual('echo 4',
                         split_results[3].strip(),
                         'Test the last command in the list ran last')

    def test_7_list_command_with_passthrough(self):
        """Test that passthrough args are correctly run in list commands
        """
        result = subprocess.run([self.yaml_runner_script,
                                 '--config',
                                 self.test_config_path,
                                 'list_passthrough',
                                 'This',
                                 'is',
                                 'a',
                                 'test'],
                                text=True,
                                stdout=subprocess.PIPE,
                                check=False)
        self.assertEqual(result.returncode, 0, 'Test the exit code is zero')
        split_results = result.stdout.splitlines()
        self.assertEqual('echo 1',
                         split_results[0].strip(),
                         'Test the first command in the list ran first')
        self.assertEqual('This is a test',
                         split_results[1].strip(),
                         'Test the second command in the list ran with the passthrough arg')
        self.assertEqual('echo 2',
                         split_results[2].strip(),
                         'Test the third command in the list ran third')
        self.assertEqual('This is a test',
                         split_results[3].strip(),
                         'Test the last command in the list ran with the passthrough arg')

    def test_8_fail_fast_list(self):
        """Test that list commands are run correctly
        """
        result = subprocess.run([self.yaml_runner_script,
                                 '--config',
                                 self.test_config_path,
                                 'fail_fast'],
                                text=True,
                                stdout=subprocess.PIPE,
                                check=False)
        self.assertNotEqual(result.returncode, 0, 'Test the exit code is non-zero')
        split_results = result.stdout.splitlines()
        self.assertEqual('echo 1',
                         split_results[0].strip(),
                         'Test the first command in the list ran first')
        self.assertEqual('echo 2',
                         split_results[1].strip(),
                         'Test the second command in the list ran second')
        self.assertNotIn('echo 4',
                         result.stdout,
                         'Test the last command in the list did not run.')

if __name__ == '__main__':
    unittest.main()
