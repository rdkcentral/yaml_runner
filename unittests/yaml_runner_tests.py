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
"""Unit tests for YamlRunner class.

This module tests the core YamlRunner functionality including:
- Initialization with different config types (dict, file path, file object)
- Hierarchical vs simple engine selection
- Config property getter/setter
- Command execution
- Error handling
"""

import io
import unittest
from unittest.mock import patch, MagicMock, call
import tempfile
import os

from yaml_runner import YamlRunner


class TestYamlRunnerInit(unittest.TestCase):
    """Test YamlRunner initialization."""

    def setUp(self):
        """Set up test fixtures."""
        self.simple_config = {
            'commands': {
                'test_cmd': {
                    'command': 'echo "test"',
                    'description': 'Test command'
                }
            }
        }

    def test_init_with_dict_simple_engine(self):
        """Test initialization with dict config and simple engine."""
        runner = YamlRunner(self.simple_config, program='test_prog', hierarchical=False)
        
        self.assertIsNotNone(runner)
        self.assertEqual(runner._program, 'test_prog')
        self.assertTrue(runner._fail_fast)
        self.assertIsInstance(runner._engine.__class__.__name__, str)
        self.assertEqual(runner._engine.__class__.__name__, 'SimpleEngine')

    def test_init_with_dict_hierarchical_engine(self):
        """Test initialization with dict config and hierarchical engine."""
        runner = YamlRunner(self.simple_config, program='test_prog', hierarchical=True)
        
        self.assertIsNotNone(runner)
        self.assertEqual(runner._program, 'test_prog')
        self.assertEqual(runner._engine.__class__.__name__, 'HierarchicalEngine')

    def test_init_with_fail_fast_false(self):
        """Test initialization with fail_fast=False."""
        runner = YamlRunner(self.simple_config, fail_fast=False)
        
        self.assertFalse(runner._fail_fast)

    def test_init_with_file_path(self):
        """Test initialization with file path string."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write('commands:\n  test: {command: "echo test", description: "test"}\n')
            temp_path = f.name
        
        try:
            runner = YamlRunner(temp_path)
            self.assertIsNotNone(runner)
            config = runner._engine.config
            self.assertIn('commands', config)
        finally:
            os.unlink(temp_path)

    def test_init_with_file_object(self):
        """Test initialization with file object."""
        yaml_content = 'commands:\n  test: {command: "echo test", description: "test"}\n'
        file_obj = io.StringIO(yaml_content)
        
        runner = YamlRunner(file_obj)
        self.assertIsNotNone(runner)
        config = runner._engine.config
        self.assertIn('commands', config)

    def test_init_with_invalid_type(self):
        """Test initialization with invalid config type raises TypeError."""
        with self.assertRaises(TypeError) as context:
            YamlRunner(12345)  # Invalid type
        
        self.assertIn('config argument must of type', str(context.exception))


class TestYamlRunnerConfigProperty(unittest.TestCase):
    """Test YamlRunner config property."""

    def setUp(self):
        """Set up test fixtures."""
        self.simple_config = {
            'commands': {
                'test_cmd': {
                    'command': 'echo "test"',
                    'description': 'Test command'
                }
            }
        }

    def test_config_getter_returns_copy(self):
        """Test that config getter returns a copy via engine."""
        runner = YamlRunner(self.simple_config)
        
        # Config is stored in engine, getter delegates to engine.config
        config1 = runner._engine.config
        config2 = runner._engine.config
        
        # Should be equal but not same object (engine returns copy)
        self.assertEqual(config1, config2)
        self.assertIsNot(config1, config2)
        
        # Note: BaseEngine.config.copy() only does shallow copy,
        # so modifying nested dict will affect both - this is current behavior

    def test_config_setter_with_dict(self):
        """Test config setter with dictionary."""
        runner = YamlRunner(self.simple_config)
        
        new_config = {
            'commands': {
                'new_cmd': {
                    'command': 'echo "new"',
                    'description': 'New command'
                }
            }
        }
        
        runner.config = new_config
        self.assertIn('new_cmd', runner._engine.config['commands'])

    def test_config_setter_with_file_path(self):
        """Test config setter with file path."""
        runner = YamlRunner(self.simple_config)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write('commands:\n  updated: {command: "echo updated", description: "updated"}\n')
            temp_path = f.name
        
        try:
            runner.config = temp_path
            self.assertIn('updated', runner._engine.config['commands'])
        finally:
            os.unlink(temp_path)

    def test_config_setter_with_file_object(self):
        """Test config setter with file object."""
        runner = YamlRunner(self.simple_config)
        
        yaml_content = 'commands:\n  from_io: {command: "echo io", description: "from io"}\n'
        file_obj = io.StringIO(yaml_content)
        
        runner.config = file_obj
        self.assertIn('from_io', runner._engine.config['commands'])


class TestYamlRunnerCommandExecution(unittest.TestCase):
    """Test YamlRunner command execution."""

    def setUp(self):
        """Set up test fixtures."""
        self.simple_config = {
            'commands': {
                'echo_test': {
                    'command': 'echo "Hello World"',
                    'description': 'Echo test'
                }
            }
        }

    @patch('yaml_runner.yaml_runner.YamlRunner._run_command')
    def test_run_single_command(self, mock_run_command):
        """Test running a single command."""
        mock_run_command.return_value = ('output\n', '', 0)
        
        runner = YamlRunner(self.simple_config)
        stdout_list, stderr_list, exit_codes = runner.run(['echo_test'])
        
        self.assertEqual(len(stdout_list), 1)
        self.assertEqual(stdout_list[0], 'output\n')
        self.assertEqual(exit_codes[0], 0)
        mock_run_command.assert_called_once()

    @patch('yaml_runner.yaml_runner.YamlRunner._run_command')
    def test_run_multiple_commands(self, mock_run_command):
        """Test running multiple commands in sequence."""
        mock_run_command.side_effect = [
            ('output1\n', '', 0),
            ('output2\n', '', 0)
        ]
        
        config = {
            'commands': {
                'multi': {
                    'command': ['echo "test1"', 'echo "test2"'],
                    'description': 'Multiple commands'
                }
            }
        }
        
        runner = YamlRunner(config)
        stdout_list, stderr_list, exit_codes = runner.run(['multi'])
        
        self.assertEqual(len(stdout_list), 2)
        self.assertEqual(mock_run_command.call_count, 2)

    @patch('yaml_runner.yaml_runner.YamlRunner._run_command')
    def test_fail_fast_stops_on_error(self, mock_run_command):
        """Test that fail_fast=True stops execution on first error."""
        mock_run_command.side_effect = [
            ('output1\n', '', 0),
            ('', 'error\n', 1),  # Command fails
            ('output3\n', '', 0)  # Should not be called
        ]
        
        config = {
            'commands': {
                'multi': {
                    'command': ['echo "test1"', 'false', 'echo "test3"'],
                    'description': 'Multiple commands'
                }
            }
        }
        
        runner = YamlRunner(config, fail_fast=True)
        stdout_list, stderr_list, exit_codes = runner.run(['multi'])
        
        # Should stop after 2nd command fails
        self.assertEqual(len(stdout_list), 2)
        self.assertEqual(exit_codes[1], 1)
        self.assertEqual(mock_run_command.call_count, 2)

    @patch('yaml_runner.yaml_runner.YamlRunner._run_command')
    def test_fail_fast_false_continues_on_error(self, mock_run_command):
        """Test that fail_fast=False continues execution after error."""
        mock_run_command.side_effect = [
            ('output1\n', '', 0),
            ('', 'error\n', 1),  # Command fails
            ('output3\n', '', 0)  # Should still be called
        ]
        
        config = {
            'commands': {
                'multi': {
                    'command': ['echo "test1"', 'false', 'echo "test3"'],
                    'description': 'Multiple commands'
                }
            }
        }
        
        runner = YamlRunner(config, fail_fast=False)
        stdout_list, stderr_list, exit_codes = runner.run(['multi'])
        
        # Should execute all 3 commands
        self.assertEqual(len(stdout_list), 3)
        self.assertEqual(exit_codes[1], 1)
        self.assertEqual(mock_run_command.call_count, 3)

    @patch('yaml_runner.yaml_runner.YamlRunner._run_command')
    def test_run_with_config_parameter(self, mock_run_command):
        """Test run() with config parameter updates config."""
        mock_run_command.return_value = ('new output\n', '', 0)
        
        initial_config = {
            'commands': {
                'old_cmd': {
                    'command': 'echo "old"',
                    'description': 'Old command'
                }
            }
        }
        
        new_config = {
            'commands': {
                'new_cmd': {
                    'command': 'echo "new"',
                    'description': 'New command'
                }
            }
        }
        
        runner = YamlRunner(initial_config)
        runner.run(['new_cmd'], config=new_config)
        
        # Config should be updated
        self.assertIn('new_cmd', runner._engine.config['commands'])
        self.assertNotIn('old_cmd', runner._engine.config['commands'])


class TestYamlRunnerInternalMethods(unittest.TestCase):
    """Test YamlRunner internal methods."""

    def setUp(self):
        """Set up test fixtures."""
        self.simple_config = {
            'commands': {
                'test': {
                    'command': 'echo "test"',
                    'description': 'Test'
                }
            }
        }

    def test_config_to_dict_with_dict(self):
        """Test _config_to_dict with dictionary input."""
        runner = YamlRunner(self.simple_config)
        result = runner._config_to_dict(self.simple_config)
        
        self.assertEqual(result, self.simple_config)
        # Dict input returns same dict object (not a copy in _config_to_dict)
        self.assertIs(result, self.simple_config)

    def test_config_to_dict_with_string_path(self):
        """Test _config_to_dict with file path string."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write('commands:\n  test: {command: "echo test", description: "test"}\n')
            temp_path = f.name
        
        try:
            runner = YamlRunner(self.simple_config)
            result = runner._config_to_dict(temp_path)
            
            self.assertIn('commands', result)
            self.assertIn('test', result['commands'])
        finally:
            os.unlink(temp_path)

    def test_config_to_dict_with_io_object(self):
        """Test _config_to_dict with IO object."""
        yaml_content = 'commands:\n  test: {command: "echo test", description: "test"}\n'
        file_obj = io.StringIO(yaml_content)
        
        runner = YamlRunner(self.simple_config)
        result = runner._config_to_dict(file_obj)
        
        self.assertIn('commands', result)
        self.assertIn('test', result['commands'])

    def test_config_to_dict_with_invalid_type(self):
        """Test _config_to_dict with invalid type raises TypeError."""
        runner = YamlRunner(self.simple_config)
        
        with self.assertRaises(TypeError) as context:
            runner._config_to_dict([1, 2, 3])  # Invalid type
        
        self.assertIn('config argument must of type', str(context.exception))

    @patch('yaml_runner.yaml_runner.subprocess.Popen')
    def test_run_command_captures_output(self, mock_popen):
        """Test _run_command captures stdout and stderr."""
        # Mock process
        mock_process = MagicMock()
        mock_process.stdout.readline.side_effect = ['output line\n', '']
        mock_process.stderr.readline.side_effect = ['error line\n', '']
        mock_process.wait.return_value = 0
        mock_popen.return_value.__enter__.return_value = mock_process
        
        runner = YamlRunner(self.simple_config)
        stdout, stderr, exit_code = runner._run_command('echo "test"')
        
        self.assertIn('output line', stdout)
        self.assertIn('error line', stderr)
        self.assertEqual(exit_code, 0)

    @patch('yaml_runner.yaml_runner.subprocess.Popen')
    def test_run_command_non_zero_exit(self, mock_popen):
        """Test _run_command with non-zero exit code."""
        mock_process = MagicMock()
        mock_process.stdout.readline.side_effect = ['']
        mock_process.stderr.readline.side_effect = ['error\n', '']
        mock_process.wait.return_value = 127
        mock_popen.return_value.__enter__.return_value = mock_process
        
        runner = YamlRunner(self.simple_config)
        stdout, stderr, exit_code = runner._run_command('nonexistent_command')
        
        self.assertEqual(exit_code, 127)

    def test_run_commands_empty_list(self):
        """Test _run_commands with empty command list."""
        runner = YamlRunner(self.simple_config)
        stdout_list, stderr_list, exit_codes = runner._run_commands([])
        
        self.assertEqual(len(stdout_list), 0)
        self.assertEqual(len(stderr_list), 0)
        self.assertEqual(len(exit_codes), 0)


class TestReadStream(unittest.TestCase):
    """Test _read_stream helper function."""

    @patch('sys.stdout')
    def test_read_stream_stdout(self, mock_stdout):
        """Test _read_stream writes to stdout."""
        from yaml_runner.yaml_runner import _read_stream
        
        mock_stream = io.StringIO('line1\nline2\n')
        result_list = []
        
        _read_stream(mock_stream, 'stdout', result_list)
        
        self.assertEqual(len(result_list), 1)
        self.assertIn('line1', result_list[0])
        self.assertIn('line2', result_list[0])

    @patch('sys.stderr')
    def test_read_stream_stderr(self, mock_stderr):
        """Test _read_stream writes to stderr."""
        from yaml_runner.yaml_runner import _read_stream
        
        mock_stream = io.StringIO('error1\nerror2\n')
        result_list = []
        
        _read_stream(mock_stream, 'stderr', result_list)
        
        self.assertEqual(len(result_list), 1)
        self.assertIn('error1', result_list[0])
        self.assertIn('error2', result_list[0])


if __name__ == '__main__':
    unittest.main()
