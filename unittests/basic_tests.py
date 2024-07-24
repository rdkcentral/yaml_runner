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
"""
This script defines the basic unit tests for the `yaml_runner` class.

The tests validate the functionalities of `yaml_runner` including:
  * Help message display
  * 'hello_word' command execution
  * 'echo_all' command execution with and without arguments
"""

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
    """
    This class defines the basic unit tests for the `yaml_runner` class.
    """
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
        """
        Setup to run before any test method is run.

        This method is called once before any of the test methods in this
        class are executed. It creates a temporary directory named 'workspace'
        in the same directory as the test script.
        """
        if path.exists(cls.workspace):
            shutil.rmtree(cls.workspace)
        os.mkdir(cls.workspace)

    @classmethod
    def setUp(cls):
        """
        Setup to run before each test method is run.

        This method is called before each test method is executed. It creates
        StringIO objects to capture the standard output and standard error streams
        during the test execution.
        """
        cls.stderr_log = io.StringIO()
        cls.stdout_log = io.StringIO()


    @classmethod
    def tearDownClass(cls) -> None:
        """
        Clean up after all tests are finished.

        This method is called after all the test methods in this class
        have been executed. It removes the temporary 'workspace' directory
        and closes the test configuration file.
        """
        shutil.rmtree(cls.workspace)
        cls.test_config_file.close()
        return super().tearDownClass()

    @classmethod
    def tearDown(cls) -> None:
        """
        Clean up after each test method has finished.

        This method is called after each test method is executed. It closes
        the StringIO objects used to capture the standard output and standard
        error streams.
        """
        cls.stdout_log.close()
        cls.stderr_log.close()

    def _run_yaml_runner(self,**kwargs):
        """
        Runs the YamlRunner with arguments and captures standard output and error.

        This method executes the `run` method of the `YamlRunner` object
        with the provided keyword arguments. It uses the `contextlib.redirect_stdout`
        and `contextlib.redirect_stderr` context managers to capture the standard
        output and standard error streams during the execution. In case of a
        `SystemExit` exception, it extracts the exit code and rewinds the captured
        output streams.

        Args:
            **kwargs: Keyword arguments to be passed to the `YamlRunner.run` method.

        Returns:
            A tuple containing three elements:
                * Captured standard output as a list of strings (one string per line).
                * Captured standard error as a list of strings (one string per line).
                * Exit code of the `YamlRunner.run` execution.
        """
        with (contextlib.redirect_stdout(self.stdout_log),
              contextlib.redirect_stderr(self.stderr_log)):
            try:
                stdout, stderr, exit_code = self.runner.run(**kwargs)
            except SystemExit as e:
                exit_code = [e.code]
                self.stdout_log.seek(0)
                self.stderr_log.seek(0)
                stdout = [self.stdout_log.read()]
                stderr = [self.stderr_log.read()]
        return stdout, stderr, exit_code

    def test_1_no_config(self):
        """
        Test to prove that when yaml_runner is run with no args it display the
        correct message.
        """
        stdout, stderr, exit_code = self._run_yaml_runner(args=['--help'])
        self.assertEqual(exit_code[0], 2, 'Test the exit code is zero')
        self.assertIn('-c', stderr[0], 'Test the -c option is in the stderr')
        self.assertIn('--config', stderr[0], 'Test the --config option is in the stderr')

    def test_2_help_with_config(self):
        """
        Test to show that yaml_runner displays the expected help message,
        for each config type.
        """
        for config_type, config in self.test_configs.items():
            self._validate_help_with_config(config, config_type)

    def _validate_help_with_config(self, config, config_type):
        """
        Tests that the YamlRunner prints the correct help message for the configuration provided.

        This method runs the `YamlRunner` with the provided configuration (`config`)
        and the `--help` argument.
        It then verifies the captured standard output to ensure it includes
        expected elements like 'COMMAND', descriptions for available choices, and help
        options (`-h` or `--help`). It also checks that the standard error is empty.

        Args:
            config: The configuration to be used for running the YamlRunner (can be a path, dictionary or file handle).
            config_type: A string describing the type of configuration provided (e.g. 'path', 'dict', 'file handle').
        """
        stdout, stderr, exit_code = self._run_yaml_runner(config=config, args=['--help'])
        self.assertEqual(exit_code[0], 0, f'Test the exit code is zero [{config_type}]')
        self.assertIn('COMMAND', stdout[0], f'Test COMMAND is in the output [{config_type}]')
        self.assertIn('hello_world',
                      stdout[0],
                      f'Test the hello_world choice is in the output [{config_type}]')
        self.assertIn('print hello world in stdout',
                      stdout[0],
                      f'Test the description of hello_world is in the output [{config_type}]')
        self.assertIn('echo_all',
                      stdout[0],
                      f'Test the echo_all choice is in the output [{config_type}]')
        self.assertIn('-h', stdout[0], f'Test the -h option is in the output [{config_type}]')
        self.assertIn('--help', stdout[0], f'Test the --help option is in the output [{config_type}]')
        self.assertEqual(stderr[0], '', f'Test the stderr is empty [{config_type}]')

    def test_3_hello_world(self):
        """
        Tests that the YamlRunner executes the 'hello_world' command successfully,
        for each config type.
        """
        for config_type, config in self.test_configs.items():
            self._validate_hello_world(config, config_type)

    def _validate_hello_world(self, config, config_type):
        """
        Tests that the YamlRunner executes the 'hello_world' command successfully.

        This method runs the YamlRunner with the 'hello_world' argument and the provided configuration.
        It then checks the captured standard output to ensure it contains the expected output ("hello world\n")
        and that the standard error is empty.

        Args:
            config: The configuration to be used for running the YamlRunner (can be a path, dictionary or file handle).
            config_type: A string describing the type of configuration provided (e.g. 'path', 'dict', 'file handle').
        """
        stdout, stderr, exit_code = self._run_yaml_runner(config=config, args=['hello_world'])
        self.assertEqual(exit_code[0], 0, f'Test the exit code is zero [{config_type}]')
        self.assertEqual('hello world\n',
                         stdout[0],
                         f'Test "hello world" is printed in stdout [{config_type}]')
        self.assertEqual(stderr[0], '', f'Test the stderr is empty [{config_type}]')

    def test_4_echo_all_help(self):
        """
        Tests that the YamlRunner prints the correct help message for
        the 'echo_all' command, for each config type.
        """
        for config_type, config in self.test_configs.items():
            self._validate_echo_all_help(config, config_type)

    def _validate_echo_all_help(self, config, config_type):
        """
        Tests that the YamlRunner print the correct help message for the 'echo_all' command.

        This method runs the `YamlRunner` with the provided configuration.
        It then verifies the captured standard output to ensure the help information
        is displayed correctly and checks that the standard error is empty.

        Args:
            config: The configuration to be used for running the YamlRunner (can be a path, dictionary or file handle).
            config_type: A string describing the type of configuration provided (e.g. 'path', 'dict', 'file handle').
        """
        stdout, stderr, exit_code = self._run_yaml_runner(config=config,
                                                          args=['echo_all', '--help'])
        self.assertEqual(exit_code[0], 0, f'Test the exit code is zero [{config_type}]')
        self.assertIn('echo_all',
                      stdout[0],
                      f'Test the echo_all choice is in the output [{config_type}]')
        self.assertIn('PASSTHROUGH',
                      stdout[0],
                      f'Test PASSTHROUGH is shown as a optional argument [{config_type}]')
        self.assertIn('-h', stdout[0], f'Test the -h option is in the output [{config_type}]')
        self.assertIn('--help', stdout[0], f'Test the --help option is in the output [{config_type}]')
        self.assertEqual(stderr[0], '', f'Test the stderr is empty [{config_type}]')

    def test_5_echo_all_with_passthrough_arg(self):
        """
        Tests that the YamlRunner executes the 'echo_all' command
        with a passthrough argument, for each config type.
        """
        for config_type, config in self.test_configs.items():
            self._validate_echo_all_with_passthrough(config, config_type)

    def _validate_echo_all_with_passthrough(self, config, config_type):
        """
        Tests that the YamlRunner executes the 'echo_all' command with a passthrough argument.

        This test case runs the `YamlRunner` with the `echo_all` argument
        and a sample passthrough argument 'This is a passthrough argument'.
        It then verifies the captured standard output to ensure it contains
        the echoed passthrough argument and that the standard error is empty.

        Args:
            config: The configuration to be used for running the YamlRunner (can be a path, dictionary or file handle).
            config_type: A string describing the type of configuration provided (e.g. 'path', 'dict', 'file handle').
        """
        stdout, stderr, exit_code = self._run_yaml_runner(config=config, args=['echo_all', 'TEST'])
        self.assertEqual(exit_code[0], 0, f'Test the exit code is zero [{config_type}]')
        self.assertEqual('TEST\n',
                         stdout[0],
                         f'Test "hello world" is printed in stdout [{config_type}]')
        self.assertEqual(stderr[0], '', f'Test the stderr is empty [{config_type}]')


if __name__ == '__main__':
    unittest.main()
