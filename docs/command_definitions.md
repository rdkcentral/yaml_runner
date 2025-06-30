# Command Definitions
All keys that have a command field directly under them will be treated as a command definition by yaml_runner.<br>
The value of the command key is expected to be a string or a list of commands to be run when the parent key is called through yaml_runner.
> *Some of the behaviors of the commands can be altered by settings in the [global configuration](./global_configuration.md).*

## Optional Keys
Optionally the below keys can be included to a command section:
- **description**: The value of this key will be shown as the help message for the command when `--help` is used with yaml runner.
- **params**: This section allows parameters to be defined for the command.
  - **passthrough**: If true, then all arguments following the yaml_runner command will be substituted into the command string/s in place of the `$@`.
    > *This is currently the only parameter supported. An example for it can be found [here](#command-with-passthrough-arguments).*

## Ignored Sections
Sections in the config without a command key are ignored, except for the [Global configuration section](./global_configuration.md)

## Examples of Command Definitions
All of these examples can be tested by pasting the yaml snippet into a file called `example_config.yml` and then running the command shown.

* [Simple Command](#simple-command)
* [Command with Passthrough Arguments](#command-with-passthrough-arguments)
* [List Commands](#list-commands)
* [List Command with Passthrough Arguments](#list-command-with-passthrough-arguments)

### Simple Command
```yaml
hello_world:
  command: echo "hello world"
  description: Print hello world in stdout.
```
Example Usage:<br>
`yaml_runner -c example_config.yml run hello_world`

Expected Outcome:<br>
`hello world` is printed in the console.

### Command with Passthrough Arguments
```yaml
echo_passthrough:
  command: echo $@
  description: Print all arguments passed after echo_passthrough.
  params:
    passthrough: true
```
Example Usage:<br>
`yaml_runner -c example_config.yml echo_passthrough Hello Test User!`

Expected Outcome:<br>
`Hello Test User!` is printed in the console.

### List Commands
```yaml
list:
  description: Run each command listed in the command.
  command:
    - echo "echo 1"
    - echo "echo 2"
    - echo "echo 3"
    - echo "echo 4"
```
> *If a command fails in a list command, yaml runner will exit with the highest non-zero exit code.*

Example Usage:<br>
`yaml_runner -c example_config.yml list`

Expected Outcome:<br>
The following should be printed in the console.
```
echo 1
echo 2
echo 3
echo 4
```

### List Command with Passthrough Arguments
```yaml
list_passthough:
  description: Run each command listed, substituting the extra args in.
  command:
    - echo "echo 1"
    - echo "$@"
    - echo "echo 2"
    - echo "$@"
  params:
    passthrough: true
```

Example Usage:<br>
`yaml_runner -c example_config.yml list_passthrough Hello Test User!`

Expected Outcome:<br>
The follow should be printed in the console.
```
echo 1
Hello Test User!
echo 2
Hello Test User
```
