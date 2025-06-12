# YamlRunner Module Reference

## YamlRunner(config: dict | IOBase | str, program: str = '', hierarchical: bool = False, fail_fast=True)
YamlRunner class for executing commands from a YAML configuration file.

This class provides a framework for running commands defined within a YAML
configuration file. It processes a YAML configuration and sets up argument
parsers, allowing the commands from the yaml to be executed..

* **Parameters:**
  * **config** (*dict* | *io.IOBase* | *str*) – Yaml configuration of commands that can be run. Defaults to None.
  * **program** (*str*, optional) - Program name. Defaults to an empty string.
  * **hierarchical** (*bool*, optional): Process the yaml hierarchically. Defaults to False.
  * **fail_fast** (*bool*, optional): Prevent command list from continuing after a command has failed. Defaults to True.

### *property* config *: dict*

A copy of the config currently in use by the YamlRunner

### run(args: list[str], config: dict | IOBase | str = None) → tuple

This function runs a script with specified configuration and arguments, processing command line
arguments and executing commands.

* **Parameters:**
  * **args** (*list*) – The arguments passed to the script. Defaults to None.
    If None, external args are processed and used instead.
  * **config** (*dict* | *io.IOBase* | *str*) – Yaml configuration of commands that can be run. Defaults to None.
    If None, config is expected to be passed in from command line with –config option.
* **Returns:**
  Returns a tuple containing three lists: stdout_list, stderr_list, and exit_code_list.<br>
  Each list contains the respective outputs (stdout, stderr,
    and exit code) of running the command(s) specified in the self.commands attribute.
* **Return type:**
  tuple