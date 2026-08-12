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
import unittest

from yaml_runner.config_readers.hierarchical_config_reader import HierarchicalConfigReader
from yaml_runner.exceptions import ConfigValidationError
from yaml_runner.models import FlagNode, OptionNode

class HierarchicalConfigReaderTests(unittest.TestCase):
    def test_reads_config_hierarchy(self):
        config = {
            "group": {
                "command1": {
                    "command": "echo hello"
                },
                "command2": {
                    "command": "echo goodbye"
                }
            }
        }

        commands = HierarchicalConfigReader(config).get_commands()

        self.assertEqual(commands["group"].subcommands["command1"].command, ["echo hello"])
        self.assertEqual(commands["group"].subcommands["command2"].command, ["echo goodbye"])

    def test_command_group_can_take_flags(self):
        config = {
            "group": {
                "flags": {
                    "aflag": {
                        "short": "a",
                        "value": "sub_this_in"
                    }
                },
                "hello": {
                    "command": "echo {{aflag}}"
                }
            }
        }

        commands = HierarchicalConfigReader(config).get_commands()

        self.assertIsInstance(commands["group"].flags["aflag"], FlagNode)
        self.assertEqual(commands["group"].flags["aflag"].short, "a")
        self.assertEqual(commands["group"].flags["aflag"].value, "sub_this_in")

    def test_command_group_can_take_options(self):
        config = {
            "group": {
                "options": {
                    "anoption": {
                        "short": "a",
                        "description": "an option"
                    }
                },
                "hello": {
                    "command": "echo {{anoption}}"
                }
            }
        }

        commands = HierarchicalConfigReader(config).get_commands()

        self.assertIsInstance(commands["group"].options["anoption"], OptionNode)
        self.assertEqual(commands["group"].options["anoption"].short, "a")
        self.assertEqual(commands["group"].options["anoption"].description, "an option")

    def test_command_groups_cant_take_arguments(self):
        config = {
            "group": {
                "arguments": {
                    "invalid_argument": {
                        "description": "this should be invalid as it belongs to a group"
                    }
                },
                "hello": {
                    "command": "echo {{anoption}}"
                }
            }
        }

        with self.assertRaises(ConfigValidationError):
            HierarchicalConfigReader(config).get_commands()

    def test_commands_with_subcommands_cant_take_arguments(self):
        config = {
            "command_with_sub": {
                "command": "echo I have a subcommand",
                "arguments": {
                    "invalid_argument": {
                        "description": "A command with a subcommand cant take arguments"
                    }
                },
                "sub": {
                    "command": "echo hello"
                }
            }
        }

        with self.assertRaises(ConfigValidationError):
            HierarchicalConfigReader(config).get_commands()

    def test_a_tree_cant_contain_duplicate_flags(self):
        config = {
            "dupe_flag_tree": {
                "flags": {
                    "aflag": {
                        "value": "duplicate"
                    }
                },
                "acommand": {
                    "command": "echo hello {{aflag}}",
                    "flags": {
                        "aflag": {
                            "value": "bad_flag"
                        }
                    }
                }
            }
        }

        with self.assertRaises(ConfigValidationError):
            HierarchicalConfigReader(config).get_commands()

    def test_a_tree_cant_contain_duplicate_options(self):
        config = {
            "dupe_option_tree": {
                "options": {
                    "anoption": {
                        "description": "duplicate"
                    }
                },
                "acommand": {
                    "command": "echo hello {{anoption}}",
                    "options": {
                        "anoption": {
                            "description": "bad option"
                        }
                    }
                }
            }
        }

        with self.assertRaises(ConfigValidationError):
            HierarchicalConfigReader(config).get_commands()

    def test_separate_trees_can_contain_same_options_or_flags(self):
        config = {
            "tree1": {
                "options": {
                    "anoption": {
                        "description": "an option"
                    }
                },
                "command1": {
                    "command": ["echo {{anoption}}", "echo {{aflag}}"],
                    "flags": {
                        "aflag": {
                            "value": "avalue"
                        }
                    }
                }
            },
            "tree2": {
                "options": {
                    "anoption": {
                        "description": "an option"
                    }
                },
                "command2": {
                    "command": ["echo {{anoption}}", "echo {{aflag}}"],
                    "flags": {
                        "aflag": {
                            "value": "avalue"
                        }
                    }
                }
            },
        }

        HierarchicalConfigReader(config).get_commands()

    def test_tree_cant_contain_duplicate_short_options(self):
        config = {
            "group": {
                "options": {
                    "first": {
                        "short": "x"
                    }
                },
                "command": {
                    "command": "echo hello",
                    "options": {
                        "second": {
                            "short": "x"
                        }
                    }
                }
            }
        }

        with self.assertRaises(ConfigValidationError):
            HierarchicalConfigReader(config).get_commands()

    def test_sibling_commands_can_reuse_options(self):
        config = {
            "group": {
                "command1": {
                    "command": "echo one",
                    "options": {
                        "foo": {}
                    }
                },
                "command2": {
                    "command": "echo two",
                    "options": {
                        "foo": {}
                    }
                }
            }
        }

        HierarchicalConfigReader(config).get_commands()

    def test_command_group_preserves_description(self):
        config = {
            "group": {
                "description": "Group description",
                "hello": {
                    "command": "echo hello"
                }
            }
        }

        commands = HierarchicalConfigReader(config).get_commands()

        self.assertEqual(
            commands["group"].description,
            "Group description"
        )

if __name__ == "__main__":
    unittest.main()
