# Global Configuration
Global configuration for yaml_runner can be set in the configs by defining a yaml_runner section.<br>
> *If this section is left empty or does not exist for in the config, the default for each option is used.*

Below are the currently supported options of the global configuration of yaml_runner.
- [`fail_fast`](#example-fail-fast-behavior): If true, the runner stops executing a list of commands upon the first failure. If false, it continues regardless of errors.
  - Default is true.
- [`hierarchical`](#example-of-hierarchical-command-behaviour): If true, nested keys are treated as subcommands, requiring full paths to execute them.
  - Default is false.

## Example of a global configuration section using default settings.
```yaml
yaml_runner:
  fail_fast: true
  hierarchical: false
```

## Example Fail-Fast Behavior
```yaml
yaml_runner:
  fail_fast: true

fail_fast:
  description: Run each command listed, stopping at the third command.
  command:
    - echo "echo 1"
    - echo "echo 2"
    - this_isnt_a_real_command # Invalid command
    - echo "echo 4"
```
**Example command:**
`yaml_runner -c example_config fail_fast`

**If fail_fast is true**<br>
`echo 1` and `echo 2` should print into the console, before `this_isnt_a_real_command` is attempted and fails. The failure should cause yaml_runner to exit with a non-zero exit code and `echo 4` should not be printed in the console.
> *This is the default behaviour for yaml_runner.*

**If fail_fast is false**<br>
`echo 1` and `echo 2` should print into the console, before `this_isnt_a_real_command` is attempted and fails. yaml_runner should then continue to process the commands, causing `echo 4` to be printed into the console before exiting with a non-zero exit code.

## Example of Hierarchical Command Behaviour
```yaml
yaml_runner:
  hierarchical: true

run:
  example:
    description: Example of how nested commands work.
    nested:
      description: Run the nested command.
      command: echo "This is the nested command"
```
**Example command:**
`yaml_runner run example nested`

**If hierarchical is true**<br>
`This is the nested command` should be printed in the console.

**If hierarchical is false**<br>
yaml_runner should print a message stating that `run` is an invalid choice, showing that the valid command is `nested`.
> *This is the default behaviour for yaml_runner.*