<div style="text-align:center"><img src="docs/images/YAML_Runner_Logo_250.png"/></div>

# Yaml Runner

Yaml Runner is a python library that provides a command-line interface to run commands stored in a yaml file.


## Installatation

```
pip install git+https://github.com/rdkcentral/yaml_runner.git@master
```

## Usage

The simplest usages for this library is to use it to run it in a main function. See [yaml_runner_run.py](examples/yaml_runner_run.py)

However, for more advanced usage this library can be extended. The simplest way to do this is to inherit it in a class and extend it there.

## Documentation

Here is an example of a yaml config that will run with yaml_runner [test_config.yml](examples/test_config.yml). It has comments explaining how the sections are used.
This config can be tested with the [yaml_runner_run.py](examples/yaml_runner_run.py) by running the following commands.
```sh
git clone https://github.com/rdkcentral/yaml_runner.git
cd yaml_runner/examples
./yaml_runner_run.py --config test_config.yml --help
```

## Contributing

See contributing file: [CONTRIBUTING.md](CONTRIBUTING.md)

## License

See license file: [LICENSE](LICENSE)
