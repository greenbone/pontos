(development)=

# Development

**pontos** uses [poetry](https://python-poetry.org/) for its own dependency management and build
process.

First install poetry via pip

```shell
python3 -m pip install --user poetry
```

Afterwards run

```shell
poetry install
```

in the checkout directory of **pontos** (the directory containing the
`pyproject.toml` file) to install all dependencies including the packages only
required for development.

Afterwards activate the git hooks for auto-formatting and linting via [autohooks](https://github.com/greenbone/autohooks/).

```shell
poetry run autohooks activate
```

Validate the activated git hooks by running

```shell
poetry run autohooks check
```
