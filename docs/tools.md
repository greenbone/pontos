(tools)=

# Tools and Utilities <!-- omit in toc -->


{program}`pontos` comes with a continuously increasing set of features.
The following commands are currently available:

- [pontos-release](#pontos-release)
- [pontos-version](#pontos-version)
- [pontos-update-header](#pontos-update-header)
- [pontos-changelog](#pontos-changelog)
- [pontos-github](#pontos-github)
- [pontos-github-script](#pontos-github-script)
- [pontos-nvd-cve](#pontos-nvd-cve)
- [pontos-nvd-cves](#pontos-nvd-cves)
- [pontos-nvd-cpe](#pontos-nvd-cpe)
- [pontos-nvd-cpes](#pontos-nvd-cpes)

## pontos-release

`pontos-release` - Release handling utility for C/C++ (CMake),
JavaScript/TypeScript, Golang and Python Projects.

:::{note}
We also provide easy-to-use [GitHub Action](https://github.com/greenbone/actions/),
to create [releases ](https://github.com/greenbone/actions/tree/main/release)
that we recommended to use instead of manually releasing with pontos-release.
:::

```shell
# Release the next patch version (x.x.1) of project <foo>, using conventional
# commits for release notes, pushes the changes and release notes
pontos-release release --project <foo> --release-type patch
# Sign a release:
pontos-release sign --project <foo> --release-version 1.2.3
--signing-key 1234567890ABCDEFEDCBA0987654321 [--passphrase <for_that_key>]
```

## pontos-version

`pontos-version` - Version handling utility for C, Go and Python Projects

```shell
# Update version of this project to 22.1.1
pontos-version update 22.1.1
# Show current projects version
pontos-version show
# Verify the current version information
pontos-version verify current
# calculate the next minor release version
pontos-version next minor
```

**Supported config files:**
* CMake: `CMakeLists.txt`
* Python: `pyproject.toml` and an arbitrary version module
* Golang: `go.md` and `version.go`
* JavaScript/TypeScript: `package.json`, `src/version.js` and `src/version.ts`

## pontos-update-header

`pontos-update-header` - Handling Copyright header for various file types and licenses

:::{note}
We also provide easy-to-use [GitHub Actions](https://github.com/greenbone/actions/#usage), that updates copyright year in header of files and creates a Pull Request.
:::

```shell
# Update year in Copyright header in files based on last commit in corresponding repo,
also add missing headers
pontos-update-header -d <dir1> <dir2>
```

**Supported files:**
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
`.txt`
`.xml`
`.xsl`

**Supported licenses:**
`AGPL-3.0-or-later`
`GPL-2.0-only`
`GPL-2.0-or-later`
`GPL-3.0-or-later`

**Copyright header schema:** `Copyright (C) 2020-2022 Greenbone AG`

## pontos-changelog

`pontos-changelog` - Parse conventional commits in the current branch and create
a changelog from the commit messages.

```shell
# Parse conventional commits and create <changelog_file>
pontos-changelog -o <changelog-file>
# Parse conventional commits between git tag 1.2.3 and 2.0.0 and print changelog to the console
pontos-changelog --current-version 1.2.3 --next-version 2.0.0
```

## pontos-github

`pontos-github` - Handling GitHub operations, like Pull Requests (beta)

```shell
# create a PR on GitHub
pontos-github pr create <orga/repo> <head> <target> <pr_title> [--body <pr_body>]
# update a PR on GitHub
pontos-github pr update <orga/repo> <pr> [--target <target_branch>] [--title <pr_title>]        [--body <pr_body>]
# get modified and deleted files in a PR, store in file test.txt
pontos-github FS <orga/repo> <pull_request> -s modified deleted -o test.txt
# add labels to an Issue/PR
pontos-github L <orga/repo> <issue/PR> label1 label2
```

## pontos-github-script

`pontos-github-script` - Run Python scripts for GitHub automation.

A number of useful GitHub scripts are available in the [pontos repository](https://github.com/greenbone/pontos/tree/main/pontos/github/scripts).

```sh
# List all members of a GitHub Organization
pontos-github-script --token <ghp_XYZ> scripts/github/members.py <organization>
```

## pontos-nvd-cve

`pontos-nvd-cve` - Get information about a single CVE

```shell
# query a cve
pontos-nvd-cve CVE-2021-38397
```

## pontos-nvd-cves

`pontos-nvd-cves` - Search for specific CVEs

```shell
# get all cves with a specific keyword
pontos-nvd-cves --keywords mac apple
```

## pontos-nvd-cpe

`pontos-nvd-cpe` - Get information about a single CPE

```shell
pontos-nvd-cpe "9F5DB8E0-14E4-40EC-B567-CF1108EEE735"
```

## pontos-nvd-cpes

`pontos-nvd-cpes` - Search for specific CPEs

```shell
# get all cpes for a specific keyword
pontos-nvd-cpes --keywords macos
```
