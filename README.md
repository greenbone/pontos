![Greenbone Logo](https://www.greenbone.net/wp-content/uploads/gb_logo_resilience_horizontal.png)

# Pontos - Greenbone Python Utilities and Tools <!-- omit in toc -->

[![GitHub releases](https://img.shields.io/github/release/greenbone/pontos.svg)](https://github.com/greenbone/pontos/releases)
[![PyPI release](https://img.shields.io/pypi/v/pontos.svg)](https://pypi.org/project/pontos/)
[![code test coverage](https://codecov.io/gh/greenbone/pontos/branch/master/graph/badge.svg)](https://codecov.io/gh/greenbone/pontos)
[![Build and test](https://github.com/greenbone/pontos/actions/workflows/ci-python.yml/badge.svg)](https://github.com/greenbone/pontos/actions/workflows/ci-python.yml)

The **pontos** Python package is a collection of utilities, tools, classes and
functions maintained by [Greenbone Networks].

Pontos is the German name of the Greek titan [Pontus](https://en.wikipedia.org/wiki/Pontus_(mythology)),
the titan of the sea.

## Table of Contents <!-- omit in toc -->

- [Tools](#tools-and-utilities)
- [Installation](#installation)
  - [Requirements](#requirements)
  - [Install using pip](#install-using-pip)
  - [Install using poetry](#install-using-poetry)
- [Development](#development)
- [Maintainer](#maintainer)
- [Contributing](#contributing)
- [License](#license)

## Tools and Utilities

`pontos` comes with a continiously increasing set of features.
The following commands are currently available:

* `pontos-release` - Release handling utility for C and Python Projects
>We also provide easy-to-use [GitHub Actions](https://github.com/greenbone/actions/#usage), that we recommended to use instead of manually releasing with pontos-release.
```bash
# Prepare the next patch release (x.x.2) of project <foo>, use conventional commits for release notes
pontos-release prepare --project <foo> -patch -CC
# Release that patch version of project <foo>
pontos-release release --project <foo>
# Sign a release:
pontos-release sign --project <foo> --release-version 1.2.3 --signing-key 1234567890ABCDEFEDCBA0987654321 [--passphrase <for_that_key>]
```
* `pontos-version` - Version handling utility for C, Go and Python Projects
```bash
# Update version of this project to 22.1.1
pontos-version update 22.1.1
# Show current projects version
pontos-version show
```
* `pontos-update-header` - Handling Copyright header for various file types and licences
>We also provide an easy-to-use [GitHub Action](https://github.com/greenbone/actions/#usage), that updates copyright year in header of files and creates a Pull Request.
```bash
# Update year in Copyright header in files, also add missing headers
pontos-update-header -d <dir1> <dir2>
```
* `pontos-changelog` - Parse conventional commits in the current branch, creating CHANGELOG.md file
```bash
# Parse conventional commits and create <changelog_file>
pontos-changelog -o <changelog-file>
```
* pontos-github` - Handling GitHub operations, like Pull Requests (beta)
```bash
# create a PR on GitHub
pontos-github pr <orga/repo> <head> <target> <pr_title> [--body <pr_body>]
# get modified and deleted files in a PR, store in file test.txt
pontos-github FS <orga/repo> <pull_request> -s modified deleted -o test.txt
```

* pontos` also comes with a Terminal interface printing prettier outputs
```python
import pontos.terminal.terminal

term = terminal.Terminal()
with term.indent():
    term.ok("Hello indented World")
```
* `pontos` also comes with git and GitHub APIs
```python
import pontos.git
import pontos.github
```

## Installation

### Requirements

Python 3.7 and later is supported.

### Install using pip

pip 19.0 or later is required.

> **Note**: All commands listed here use the general tool names. If some of
> these tools are provided by your distribution, you may need to explicitly use
> the Python 3 version of the tool, e.g. **`pip3`**.

You can install the latest stable release of **pontos** from the Python
Package Index (pypi) using [pip]

    pip install --user pontos

### Install using poetry

Because **pontos** is a Python library you most likely need a tool to
handle Python package dependencies and Python environments. Therefore we
strongly recommend using [pipenv] or [poetry].

You can install the latest stable release of **pontos** and add it as
a dependency for your current project using [poetry]

    poetry add pontos

For installation via pipenv please take a look at their [documentation][pipenv].

## Development

**pontos** uses [poetry] for its own dependency management and build
process.

First install poetry via pip

    pip install --user poetry

Afterwards run

    poetry install

in the checkout directory of **pontos** (the directory containing the
`pyproject.toml` file) to install all dependencies including the packages only
required for development.

Afterwards activate the git hooks for auto-formatting and linting via
[autohooks].

    poetry run autohooks activate

Validate the activated git hooks by running

    poetry run autohooks check

## Maintainer

This project is maintained by [Greenbone Networks GmbH][Greenbone Networks]

## Contributing

Your contributions are highly appreciated. Please
[create a pull request](https://github.com/greenbone/pontos/pulls)
on GitHub. Bigger changes need to be discussed with the development team via the
[issues section at GitHub](https://github.com/greenbone/pontos/issues)
first.

## License

Copyright (C) 2020-2021 [Greenbone Networks GmbH][Greenbone Networks]

Licensed under the [GNU General Public License v3.0 or later](LICENSE).

[Greenbone Networks]: https://www.greenbone.net/
[poetry]: https://python-poetry.org/
[pip]: https://pip.pypa.io/
[pipenv]: https://pipenv.pypa.io/
[autohooks]: https://github.com/greenbone/autohooks
