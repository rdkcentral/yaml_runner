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

import contextlib
import io
import os
from os import path
import shutil
import sys
import unittest

import yaml
try:
	from yaml import CSafeLoader as SafeLoader
except ImportError:
	from yaml import SafeLoader

MY_PATH = path.abspath(__file__)
MY_DIR = path.dirname(MY_PATH)

sys.path.append(path.join(MY_DIR,'../src'))
from yaml_runner import YamlRunner

YAMLRUNNER_PATH = path.abspath(path.join(MY_DIR,'../source/yaml_runner.py'))

class BasicTest(unittest.TestCase):
    workspace = path.join(MY_DIR,'workspace')
    test_config_path = path.join(MY_DIR,'../examples/test_config.yml')
    test_config_file = open(test_config_path, 'r', encoding='utf-8')
    test_dict = yaml.load(test_config_file, SafeLoader)
    test_configs = {'path': test_config_path,
                    'dict' : test_dict,
                    'file handle' : test_config_file}
    stderr_log = None
    stdout_log = None
    runner = YamlRunner('BasicTest')

    @classmethod
    def setUpClass(cls):
        if path.exists(cls.workspace):
            shutil.rmtree(cls.workspace)
        os.mkdir(cls.workspace)

    @classmethod
    def setUp(cls):
        cls.stderr_log = io.StringIO()
        cls.stdout_log = io.StringIO()


    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(cls.workspace)
        cls.test_config_file.close()
        return super().tearDownClass()

    @classmethod
    def tearDown(cls) -> None:
        cls.stdout_log.close()
        cls.stderr_log.close()

    def _run_yaml_runner(self,**kwargs):
        with contextlib.redirect_stdout(self.stdout_log), contextlib.redirect_stderr(self.stderr_log):
            try:
                stdout, stderr, exit_code = self.runner.run(**kwargs)
            except SystemExit as e:
                exit_code = e.code
                self.stdout_log.seek(0)
                self.stderr_log.seek(0)
                stdout = self.stdout_log.read()
                stderr = self.stderr_log.read()
        return stdout, stderr, exit_code

    def test_1_no_config(self):
        stdout, stderr, exit_code = self._run_yaml_runner(args=['--help'])
        self.assertEqual(exit_code, 2, 'Test the exit code is zero')
        self.assertIn('-c', stderr, 'Test the -c option is in the stderr')
        self.assertIn('--config', stderr, 'Test the --config option is in the stderr')

    def test_2_help_with_config(self):
        for config_type, config in self.test_configs.items():
            self._test_help_with_config(config, config_type)

    def _test_help_with_config(self, config, config_type):
        stdout, stderr, exit_code = self._run_yaml_runner(config=config, args=['--help'])
        self.assertEqual(exit_code, 0, f'Test the exit code is zero [{config_type}]')
        self.assertIn('COMMAND', stdout, f'Test COMMAND is in the output [{config_type}]')
        self.assertIn('hello_world', stdout, f'Test the hello_world choice is in the output [{config_type}]')
        self.assertIn('print hello world in stdout', stdout, f'Test the description of hello_world is in the output [{config_type}]')
        self.assertIn('echo_all', stdout, f'Test the echo_all choice is in the output [{config_type}]')
        self.assertIn('-h', stdout, f'Test the -h option is in the output [{config_type}]')
        self.assertIn('--help', stdout, f'Test the --help option is in the output [{config_type}]')
        self.assertEqual(stderr, '', f'Test the stderr is empty [{config_type}]')

    def test_3_hello_world(self):
        for config_type, config in self.test_configs.items():
            self._test_hello_world(config, config_type)

    def _test_hello_world(self, config, config_type):
        stdout, stderr, exit_code = self._run_yaml_runner(config=config, args=['hello_world'])
        self.assertEqual(exit_code[0], 0, f'Test the exit code is zero [{config_type}]')
        self.assertEqual('hello world\n',stdout[0], f'Test "hello world" is printed in stdout [{config_type}]')
        self.assertEqual(stderr[0], '', f'Test the stderr is empty [{config_type}]')

    def test_4_echo_all_help(self):
        for config_type, config in self.test_configs.items():
            self._test_echo_all(config, config_type)

    def _test_echo_all(self, config, config_type):
        stdout, stderr, exit_code = self._run_yaml_runner(config=config, args=['echo_all', '--help'])
        self.assertEqual(exit_code, 0, f'Test the exit code is zero [{config_type}]')
        self.assertIn('echo_all', stdout, f'Test the echo_all choice is in the output [{config_type}]')
        self.assertIn('PASSTHROUGH', stdout, f'Test PASTHROUGH is shown as a optional argument [{config_type}]')
        self.assertIn('-h', stdout, f'Test the -h option is in the output [{config_type}]')
        self.assertIn('--help', stdout, f'Test the --help option is in the output [{config_type}]')
        self.assertEqual(stderr, '', f'Test the stderr is empty [{config_type}]')

    def test_5_echo_all_with_passthrough_arg(self):
        for config_type, config in self.test_configs.items():
            self._test_echo_all_with_passthrough(config, config_type)

    def _test_echo_all_with_passthrough(self, config, config_type):
        stdout, stderr, exit_code = self._run_yaml_runner(config=config, args=['echo_all', 'TEST'])
        self.assertEqual(exit_code[0], 0, f'Test the exit code is zero [{config_type}]')
        self.assertEqual('TEST\n',stdout[0], f'Test "hello world" is printed in stdout [{config_type}]')
        self.assertEqual(stderr[0], '', f'Test the stderr is empty [{config_type}]')


if __name__ == '__main__':
    unittest.main()
