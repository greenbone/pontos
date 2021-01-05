# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
### Changed
### Deprecated
### Removed
### Fixed

[Unreleased]: https://github.com/greenbone/pontos/compare/v0.3.1...HEAD


## [0.3.1] - 2021-01-05
### Added
- add handling of PROJECT_DEV_VERSION in CMakeLists.txt if set [#32](https://github.com/greenbone/pontos/pull/32)
### Changed
- set releasename to projectname version [#25](https://github.com/greenbone/pontos/pull/25)
- separate signing tar and zipballs from release into a own command `sign` [#33](https://github.com/greenbone/pontos/pull/33)
### Fixed
- project_dev handling was not working when there was a command after the set[#33](https://github.com/greenbone/pontos/pull/33)
- use git-signing-key instead of signing-key on commit [42](https://github.com/greenbone/pontos/pull/42)
- HEAD was not identified in changelog [51](https://github.com/greenbone/pontos/pull/51)

[0.3.1]: https://github.com/greenbone/pontos/compare/v0.3.0...HEAD

## [0.3.0] - 2020-08-19

### Added

* Add possibility to update the version within a cmake project.
* Add possibility to execute version script via poetry run version
* Add CHANGELOG.md handling (updating unreleased, get unreleased information)
* Add release command to make a release
* Add prepare release command

### Changed

* `__main__` checks if there is CMakeLists.txt or pyproject.toml in path.
   Based on that it decide which version command it will execute.

[0.3.0]: https://github.com/greenbone/pontos/compare/v0.2.0...v0.3.0

## [0.2.0] - 2020-04-14

### Changed

* Specify the path to the version file in the `pyproject.toml` and not in a
  derived `VersionCommand` anymore. This will allow to use pontos version as
  a development dependency only [#2](https://github.com/greenbone/pontos/pull/2)

[0.2.0]: https://github.com/greenbone/pontos/compare/v0.1.0...v0.2.0

## 0.1.0 - 2020-04-09

Initial release
