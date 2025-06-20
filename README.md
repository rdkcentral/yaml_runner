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
Once pip installed the `yaml_runner` command will be available. This command will required a config to specific following the `-c` option.<br>
See the [Quick Start Section](#quick-start) below for more information.

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
