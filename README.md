<div style="text-align:center"><img src="docs/images/YAML_Runner_Logo_250.png"/></div>

# Yaml Runner
Yaml Runner is a command-line interface to run commands stored in a yaml file.


## Installation
Python 3.10 or above is required by yaml_runner.

```
pip install git+https://github.com/rdkcentral/yaml_runner.git@master
```

## Usage

### CLI Usage
Once pip installed the `yaml_runner` command will be available. This command will require a config to specific following the `-c` option.<br>
See the [Quick Start Section](#quick-start) below for more information.

### Bash Completion Usage
Yaml Runner provides shell completion using two project files:
* [data/yaml_runner_bash_completion.sh](./data/yaml_runner_bash_completion.sh): Bash completion entrypoint. It inspects `COMP_WORDS`, extracts the config from `-c/--config`, and invokes `yaml_runner` in completion mode.
* [src/yaml_runner/yaml_runner_completion.py](./src/yaml_runner/yaml_runner_completion.py): Python completion bridge. It maps `_YAML_RUNNER_COMPLETE` to `_ARGPARSE_COMPLETE` and returns completion candidates from `argparse_completion`.

How they work together:
1. Bash calls `_yaml_runner_completion` from `yaml_runner_bash_completion.sh` when you press tab after `yaml_runner ...`.
2. The script exports completion environment variables and runs `yaml_runner` with `_YAML_RUNNER_COMPLETE=complete_bash`.
3. The CLI code calls `get_completion(...)` from `yaml_runner_completion.py` to generate the final suggestions.

#### Install completion for bash
Use the provided installer entrypoint (recommended):

```bash
yaml_runner_install
source ~/.bashrc
```

Or source the script directly:

```bash
source /path/to/yaml_runner/data/yaml_runner_bash_completion.sh
```

#### Completion examples
Assuming a valid config file at `./examples/simple_config.yml`:

```bash
# Suggests top-level options/commands
yaml_runner -c ./examples/simple_config.yml <TAB>

# Suggests command parameters for the selected command
yaml_runner -c ./examples/simple_config.yml simple-command <TAB>
```

If no valid `-c/--config` file is present in the current command line, completion output is intentionally limited.

### Library Usage
Yaml Runner can also be used in scripts by importing the YamlRunner module.<br>
See the [yaml_runner module reference](./docs/reference/yaml_runner.md) for more information about this.

## Documentation

### Quick Start
* Follow the [installation instructions](#installation) above.
* Create an `example_config.yml` file.
* Follow the examples in [command_definitions.md](./docs/command_definitions.md#examples-of-command-definitions)
> *Don't forget `--help` can be used with any config to show the commands available and their parameters.*

#### Example configs
Example configs that are runnable with yaml_runner are available below:
* [Simple commands config](./examples/simple_config.yml)
* [Hierarchical commands config](./examples/hierarchical_config.yml)
* [Fail fast commands config](./examples/fail_fast_config.yml)

### Reference
* [Command Definitions](./docs/command_definitions.md)
* [Global Configuration](./docs/global_configuration.md)

## Contributing

See contributing file: [CONTRIBUTING.md](CONTRIBUTING.md)

## License

See license file: [LICENSE](LICENSE)
