
## Tools and Utilities

`pontos` comes with a continiously increasing set of features.
The following commands are currently available:

#### pontos-release

* `pontos-release` - Release handling utility for C and Python Projects
>We also provide easy-to-use [GitHub Actions](https://github.com/greenbone/actions/#usage), that we recommended to use instead of manually releasing with pontos-release.
```bash
# Prepare the next patch release (x.x.2) of project <foo>, use conventional commits for release notes / commits release
pontos-release prepare --project <foo> -patch -CC
# Release that patch version of project <foo> / pushes release
pontos-release release --project <foo>
# Sign a release:
pontos-release sign --project <foo> --release-version 1.2.3 --signing-key 1234567890ABCDEFEDCBA0987654321 [--passphrase <for_that_key>]
```

pontos-release will automatically create a changelog (.md-file) when executed

#### pontos-version

* `pontos-version` - Version handling utility for C, Go and Python Projects
```bash
# Update version of this project to 22.1.1
pontos-version update 22.1.1
# Show current projects version
pontos-version show
```

Supported config files: 
`CMakeLists.txt` 
`pyproject.toml` 
`go.md` 
`package.json`

#### pontos-update-header

* `pontos-update-header` - Handling Copyright header for various file types and licences
>We also provide an easy-to-use [GitHub Action](https://github.com/greenbone/actions/#usage), that updates copyright year in header of files and creates a Pull Request.
```bash
# Update year in Copyright header in files based on last commit in corresponding repo, also add missing headers
pontos-update-header -d <dir1> <dir2>
```

Supported files:
`.bash`
`.c`
`.h`
`.go`
`.cmake`
`.js`
`.nasl`
`.po`
`.py`
`.sh`
`.txt"
`.xml`
`.xsl`

Supported licenses:
`AGPL-3.0-or-later`
`GPL-2.0-only`
`GPL-2.0-or-later`
`GPL-3.0-or-later`

Copyright header shema: `Copyright (C) 2020-2022 Greenbone Networks GmbH`

#### pontos-changelog

* `pontos-changelog` - Parse conventional commits in the current branch, creating CHANGELOG.md file
```bash
# Parse conventional commits and create <changelog_file>
pontos-changelog -o <changelog-file>
```

#### pontos-github

* `pontos-github` - Handling GitHub operations, like Pull Requests (beta)
```bash
# create a PR on GitHub
pontos-github pr create <orga/repo> <head> <target> <pr_title> [--body <pr_body>]
# update a PR on GitHub
pontos-github pr update <orga/repo> <pr> [--target <target_branch>] [--title <pr_title>] [--body <pr_body>]
# get modified and deleted files in a PR, store in file test.txt
pontos-github FS <orga/repo> <pull_request> -s modified deleted -o test.txt
# add labels to an Issue/PR
pontos-github L <orga/repo> <issue/PR> label1 label2
```

#### pontos-terminal

* `pontos` also comes with a Terminal interface printing prettier outputs
```python
import pontos.terminal.terminal

term = terminal.Terminal()
with term.indent():
    term.ok("Hello indented World")
```

#### pontos-api

* `pontos` also comes with git and GitHub APIs
```python
import pontos.git
import pontos.github
```
