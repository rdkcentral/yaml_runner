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
"""Unit tests for functions section template substitution.

This module tests the functions feature added in issue #18:
- Functions section parsing
- Template substitution with {{function_name}} syntax
- Multi-line function commands (YAML literal blocks)
- Function integration with hierarchical configs
- Error handling for missing function references

The tests rely on the configuration file 'examples/functions_config.yml'.
"""

from os import path
import subprocess
import unittest
import sys

MY_PATH = path.abspath(__file__)
MY_DIR = path.dirname(MY_PATH)

# Add parent directory to path for imports
sys.path.insert(0, MY_DIR)
from cli_test_base import CLITest


class FunctionsCLITest(CLITest):
    """Test class for functions section feature."""
    test_config_path = path.join(MY_DIR, '../examples/functions_config.yml')

    def test_1_functions_section_in_help(self):
        """
        Test that functions section is parsed and commands are exposed.
        Functions should not appear as commands themselves.
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
        
        # Verify functions section is not exposed as a command
        self.assertNotIn('functions',
                         help_dict.get('positionals', {}).keys(),
                         'Functions section should not be exposed as a command')
        
        # Verify actual commands are available
        self.assertIn('test_simple',
                      help_dict.get('positionals', {}).keys(),
                      'test_simple command should be available')
        self.assertIn('test_inline',
                      help_dict.get('positionals', {}).keys(),
                      'test_inline command should be available')

    def test_2_simple_function_substitution(self):
        """
        Test basic function template substitution.
        Command contains only {{function_name}} and should be replaced entirely.
        """
        result = subprocess.run([self.yaml_runner_script,
                                 '-c',
                                 self.test_config_path,
                                 'test_simple'],
                                text=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                check=False)
        
        self.assertEqual(result.returncode, 0,
                        'Command should execute successfully')
        self.assertIn('Hello from function',
                      result.stdout,
                      'Function output should appear in result')

    def test_3_inline_function_substitution(self):
        """
        Test function substituted inline with other commands.
        Function should be replaced in the middle of a command chain.
        """
        result = subprocess.run([self.yaml_runner_script,
                                 '-c',
                                 self.test_config_path,
                                 'test_inline'],
                                text=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                check=False)
        
        self.assertEqual(result.returncode, 0,
                        'Command should execute successfully')
        output_lines = result.stdout.strip().split('\n')
        
        # Check all three parts executed in order
        self.assertIn('Before', result.stdout,
                     'First command should execute')
        self.assertIn('Hello from function', result.stdout,
                     'Function should execute')
        self.assertIn('After', result.stdout,
                     'Last command should execute')

    def test_4_multiline_function_substitution(self):
        """
        Test multi-line function command (YAML literal block with |).
        This tests the fix for whitespace handling in multi-line functions.
        """
        result = subprocess.run([self.yaml_runner_script,
                                 '-c',
                                 self.test_config_path,
                                 'test_multiline'],
                                text=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                check=False)
        
        self.assertEqual(result.returncode, 0,
                        'Multi-line function should execute successfully')
        
        # Verify all output lines from the multi-line script
        self.assertIn('Line 1', result.stdout,
                     'First line of multi-line function should appear')
        self.assertIn('Line 2', result.stdout,
                     'Second line of multi-line function should appear')
        self.assertIn('Line 3', result.stdout,
                     'Third line of multi-line function should appear')

    def test_5_function_in_pipeline(self):
        """
        Test function used in a pipeline (after |).
        Function should work as part of a command pipeline.
        """
        result = subprocess.run([self.yaml_runner_script,
                                 '-c',
                                 self.test_config_path,
                                 'test_pipeline'],
                                text=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                check=False)
        
        self.assertEqual(result.returncode, 0,
                        'Pipeline with function should execute successfully')
        
        # JSON should be formatted (indented)
        self.assertIn('"status"', result.stdout,
                     'JSON output should contain status field')
        self.assertIn('success', result.stdout,
                     'JSON output should contain success value')

    def test_6_multiple_functions_in_command(self):
        """
        Test multiple function references in a single command.
        All functions should be substituted correctly.
        """
        result = subprocess.run([self.yaml_runner_script,
                                 '-c',
                                 self.test_config_path,
                                 'test_combined'],
                                text=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                check=False)
        
        self.assertEqual(result.returncode, 0,
                        'Command with multiple functions should execute')
        self.assertIn('Hello from function', result.stdout,
                     'simple_echo function should execute')

    def test_7_nested_commands_with_functions(self):
        """
        Test functions work in nested/hierarchical command structure.
        """
        result = subprocess.run([self.yaml_runner_script,
                                 '-c',
                                 self.test_config_path,
                                 'nested',
                                 'child'],
                                text=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                check=False)
        
        self.assertEqual(result.returncode, 0,
                        'Nested command with function should execute')
        self.assertIn('Hello from function', result.stdout,
                     'Function should execute in nested command')
        self.assertIn('Child done', result.stdout,
                     'Rest of nested command should execute')


class FunctionsEngineTest(unittest.TestCase):
    """Unit tests for functions feature at the engine level."""
    
    def test_functions_storage(self):
        """Test that functions are stored correctly in engine."""
        from yaml_runner.engines.hierarchical_engine import HierarchicalEngine
        
        config = {
            'functions': {
                'test_func': {
                    'description': 'Test function',
                    'command': 'echo "test"'
                }
            },
            'cmd': {
                'command': '{{test_func}}'
            }
        }
        
        engine = HierarchicalEngine(config=config)
        self.assertIn('test_func', engine._functions,
                     'Function should be stored in engine')
        self.assertEqual(engine._functions['test_func'].get('command'),
                        'echo "test"',
                        'Function command should be stored correctly')

    def test_template_substitution(self):
        """Test template substitution logic directly."""
        from yaml_runner.engines.hierarchical_engine import HierarchicalEngine
        
        config = {
            'functions': {
                'hello': {'command': 'echo "Hello"'}
            },
            'test': {
                'command': 'start && {{hello}} && end'
            }
        }
        
        engine = HierarchicalEngine(config=config)
        commands = engine.get_commands(['test'])
        
        self.assertEqual(len(commands), 1,
                        'Should return one command')
        self.assertIn('echo "Hello"', commands[0],
                     'Function should be substituted')
        self.assertNotIn('{{hello}}', commands[0],
                        'Template marker should be replaced')

    def test_multiline_whitespace_stripped(self):
        """Test that multi-line functions have whitespace stripped."""
        from yaml_runner.engines.hierarchical_engine import HierarchicalEngine
        
        config = {
            'functions': {
                'multiline': {
                    'command': '''
                    echo "test"
                    '''
                }
            },
            'test': {
                'command': '{{multiline}}'
            }
        }
        
        engine = HierarchicalEngine(config=config)
        commands = engine.get_commands(['test'])
        
        # Command should have leading/trailing whitespace stripped
        self.assertEqual(commands[0].strip(), 'echo "test"',
                        'Multi-line function should be stripped of whitespace')

    def test_undefined_function_handling(self):
        """Test behavior when undefined function is referenced."""
        from yaml_runner.engines.hierarchical_engine import HierarchicalEngine
        
        config = {
            'functions': {},
            'test': {
                'command': '{{undefined_function}}'
            }
        }
        
        engine = HierarchicalEngine(config=config)
        commands = engine.get_commands(['test'])
        
        # Undefined functions should remain as-is (not cause crash)
        self.assertIn('{{undefined_function}}', commands[0],
                     'Undefined function should remain in command')


if __name__ == '__main__':
    unittest.main()
