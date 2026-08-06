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
The tests also rely on a configuration file
`examples/fail_fast_config.yml`.

The tests verify the behavior of the script in the following scenarios:

* Running the script with the --config option and the list command
executes all commands in the list sequentially, confirming correct order and output.
(Test: test_1_check_list_command)

* Running the script with the --config option and the list_failure command
continues executing subsequent commands even after a failure, as fail_fast is disabled.
(Test: test_2_check_list_failure)
"""

from os import path
import subprocess
import unittest

from cli_test_base import CLITest

MY_PATH = path.abspath(__file__)
MY_DIR = path.dirname(MY_PATH)

class FailFastCLITest(CLITest):
    """Test class for the yaml_runner script."""
    test_config_path = path.join(MY_DIR, '../examples/fail_fast_config.yml')

    def test_1_check_list_command(self):
        """
        Test all commands are run from a command list in the config.
        """
        result = subprocess.run(['yaml_runner',
                                              '-c',
                                              self.test_config_path,
                                              'list'],
                                              text=True,
                                              stdout=subprocess.PIPE,
                                              stderr=subprocess.STDOUT,
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

    def test_2_check_list_failure(self):
        """
        Check that the list of commands continue to run after a failure,
        with the fail_fast option set to false.
        """
        result = subprocess.run(['yaml_runner',
                                              '-c',
                                              self.test_config_path,
                                              'list_failure'],
                                              text=True,
                                              stdout=subprocess.PIPE,
                                              stderr=subprocess.STDOUT,
                                              check=False)
        self.assertNotEqual(result.returncode, 0, 'Test the exit code is not zero')
        split_results = result.stdout.splitlines()
        self.assertEqual('echo 1',
                         split_results[0].strip(),
                         'Test the first command in the list ran first')
        self.assertIn('echo 3',
                      split_results[2].strip(),
                      'Test the third command in the list ran thrid')
        self.assertIn('echo 4',
                      split_results[-1].strip(),
                      'Test the last command in the list ran last')

if __name__ == '__main__':
    unittest.main()