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

from os import path
import subprocess
import unittest

from cli_test_base import CLITest

MY_PATH = path.abspath(__file__)
MY_DIR = path.dirname(MY_PATH)

class HierarchicalCLITest(CLITest):
    """Test class for the yaml_runner script."""
    test_config_path = path.join(MY_DIR, '../examples/hierarchical_config.yml')

    def test_1_check_hierarchical_engine_is_used(self):
        """
        Test the hierarchical engine has been used to process
        the config.
        """
        result = subprocess.run([self.yaml_runner_script,
                                              '-c',
                                              self.test_config_path,
                                              '--help'],
                                              text=True,
                                              stdout=subprocess.PIPE,
                                              stderr=subprocess.STDOUT,
                                              check=False)
        help_dict = self._help_to_dict(result.stdout)
        self.assertIn('run',
                      help_dict.get('positionals',{}).keys(),
                      'Test that the run option is in the positional args.')
        self.assertEqual('Run a command.',
                         help_dict.get('positionals',{}).get('run',''),
                         'Test the description for run is shown.')
        self.assertNotIn('unrecognised',
                         help_dict.get('positionals',{}).keys(),
                         'Test that unregonised has not been parse as a positional')
        self.assertNotIn('unrecognised_nested',
                         help_dict.get('positionals',{}).keys(),
                         'Test that unregonised has not been parse as a positional')

    def test_2_check_nesting(self):
        """
        Check that running commands following the nesting in the
        config works correctly.
        """
        result = subprocess.run([self.yaml_runner_script,
                                              '-c',
                                              self.test_config_path,
                                              'run',
                                              'example',
                                              'nested'],
                                              text=True,
                                              stdout=subprocess.PIPE,
                                              stderr=subprocess.STDOUT,
                                              check=False)
        self.assertEqual(result.returncode,
                         0,
                         'Test the command returned an 0 exit code.')
        self.assertEqual('This is the nested command',
                        result.stdout.strip(),
                        'Test the nested command printed correctly')

if __name__ == '__main__':
    unittest.main()