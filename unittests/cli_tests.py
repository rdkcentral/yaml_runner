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

This module contains unit tests for the `yaml_runner` script, which is
expected to be located at `../examples/yaml_runner_run.py` relative to this
test script. The tests also rely on a sample configuration file
`test_config.yml` located at the same path.

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
  optional arguments (e.g., `echo_all`), and the `--help` option prints the specific
  usage information for that choice.
"""


from os import path
import subprocess
import unittest

MY_PATH = path.abspath(__file__)
MY_DIR = path.dirname(MY_PATH)

class CLITest(unittest.TestCase):
    """Test class for the yaml_runner script."""
    yaml_runner_script = path.join(MY_DIR, '../examples/yaml_runner_run.py')
    test_config_path = path.join(MY_DIR, '../examples/test_config.yml')

    def test_1_no_config(self):
        """
        Tests that running the script without arguments prints the help message
        and mentions the required configuration file option.
        """
        result_no_args = subprocess.run(self.yaml_runner_script,
                                        shell=True,
                                        text=True,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE,
                                        check=False)
        result_help = subprocess.run(f'{self.yaml_runner_script} --help',
                                        shell=True,
                                        text=True,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE,
                                        check=False)
        self.assertEqual(result_help.stdout,
                         result_no_args.stdout,
                         'Test both commands return the same results')
        self.assertIn('-c', result_no_args.stderr, 'Test the -c option is in the stderr')
        self.assertIn('--config',
                      result_no_args.stderr,
                      'Test the --config option is in the stderr')

    def test_2_help_with_config(self):
        """
        Tests that running the script with --help and a valid configuration file
        prints the script's usage information.
        """
        result = subprocess.run(f'{self.yaml_runner_script} --config {self.test_config_path} --help',
                                 shell=True,
                                text=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                check=False)
        self.assertEqual(result.returncode, 0, 'Test the exit code is zero')
        self.assertIn('COMMAND', result.stdout, 'Test COMMAND is in the output')
        self.assertIn('hello_world', result.stdout, 'Test the hello_world choice is in the output')
        self.assertIn('print hello world in stdout',
                      result.stdout,
                      'Test the description of hello_world is in the output')
        self.assertIn('echo_all', result.stdout, 'Test the echo_all choice is in the output')
        self.assertIn('-h', result.stdout, 'Test the -h option is in the output')
        self.assertIn('--help', result.stdout, 'Test the --help option is in the output')
        self.assertEqual(result.stderr, '', 'Test the stderr is empty')

    def test_3_hello_world(self):
        """
        Tests that running the script with a valid choice name executes
        the corresponding function and prints the expected output.
        """
        result = subprocess.run(f'{self.yaml_runner_script} --config {self.test_config_path} hello_world',
                                shell=True,
                                text=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                check=False)
        self.assertEqual(result.returncode, 0, 'Test the exit code is zero')
        self.assertEqual('hello world\n',result.stdout, 'Test "hello world" is printed in stdout')
        self.assertEqual(result.stderr, '', 'Test the stderr is empty')

    def test_4_echo_all_help(self):
        """
        Tests that running the script with a choice supporting optional arguments
        and --help prints the specific usage information for that choice.
        """
        result = subprocess.run(f'{self.yaml_runner_script} --config {self.test_config_path} echo_all --help',
                                shell=True,
                                text=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                check=False)
        self.assertEqual(result.returncode, 0, 'Test the exit code is zero')
        self.assertIn('echo_all', result.stdout, 'Test the echo_all choice is in the output')
        self.assertIn('PASSTHROUGH',
                      result.stdout,
                      'Test PASTHROUGH is shown as an optional argument')
        self.assertIn('-h', result.stdout, 'Test the -h option is in the output')
        self.assertIn('--help', result.stdout, 'Test the --help option is in the output')
        self.assertEqual(result.stderr, '', 'Test the stderr is empty')



if __name__ == '__main__':
    unittest.main()
