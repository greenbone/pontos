# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Calendar Versioning](https://calver.org).

## [Unreleased]
### Added
### Changed
* Improve generated git commit messages for and after a release [#138](https://github.com/greenbone/pontos/pull/138)

### Deprecated
### Removed
### Fixed

[Unreleased]: https://github.com/greenbone/pontos/compare/v21.6.7...HEAD


## [21.6.7] - 2021-06-23
### Added
* Add header templates for .xsl files [#136](https://github.com/greenbone/pontos/pull/136)

### Fixed
* Correctly check if `dev` version is set in `get_current_version()`. [#137](https://github.com/greenbone/pontos/pull/137)

[21.6.7]: https://github.com/greenbone/pontos/compare/v21.6.5...v21.6.7

## [21.6.5] - 2021-06-23
### Added
* Added some output to `version` helper. [#134](https://github.com/greenbone/pontos/pull/134)
### Changed
* `pontos-release` checks now if there is a `unreleased` section in the `CHANGELOG.md` for the given release version, instead of using everything that is `unreleased`. If it doesn't find the version, it will look for a general `unreleased` section (like before). [#133](https://github.com/greenbone/pontos/pull/133)
* Improve setting dev-version after release. [#135](https://github.com/greenbone/pontos/pull/135)

### Fixed
* Fix dev-version check in CMakeLists.txt. [#135](https://github.com/greenbone/pontos/pull/135)
* The replacement of the `unreleased` section in the `CHANGELOG.md`. [#133](https://github.com/greenbone/pontos/pull/133)
  * e.g. it is able to handle `## [2.1.3] (unreleased)` now and will convert it correctly to `## [2.1.3] - 22.06.2020`

[21.6.5]: https://github.com/greenbone/pontos/compare/v21.6.4...v21.6.5

## [21.6.4] - 2021-06-22
### Added
* `pontos-release prepare` can be used with `--patch`, to create a release with the next patch version. [#131](https://github.com/greenbone/pontos/pull/131)

[21.6.4]: https://github.com/greenbone/pontos/compare/v21.6.3...v21.6.4

## [21.6.3] - 2021-06-13
### Added
* The [autohooks](https://github.com/greenbone/autohooks) Terminal to `pontos`, to have prettier console output. [#127](https://github.com/greenbone/pontos/pull/127)

[21.6.3]: https://github.com/greenbone/pontos/compare/v21.6.2...v21.6.3

## [21.6.2] - 2021-06-11
### Changed
* `pontos-release` will only sign, if key is available. If no key is given, pontos tries to lookup the key in the config.

### Fixed
* Fixed commiting when no key is available. [#118](https://github.com/greenbone/pontos/pull/118)
* Fixed releasing with pontos. A push after clearing the CHANGELOG was missing. [#110](https://github.com/greenbone/pontos/pull/110)

[21.6.2]: https://github.com/greenbone/pontos/compare/v21.6.1...v21.6.2

## [21.6.1] - 2021-06-09
### Fixed
* Fix the previous release

[21.6.1]: https://github.com/greenbone/pontos/compare/v21.6.0...v21.6.1

## [21.6.0] - 2021-06-08
### Added
- Template for header [#85](https://github.com/greenbone/pontos/pull/85)

### Changed
- For `pontos-release` the `--release-version` argument is not required anymore. You can choose between `--release-version` and `--calendar` now. [#104](https://github.com/greenbone/pontos/pull/104)
  - `--calendar` will automatically look up the next calendar release version number
  - `--release-version` can still be used for setting the release version number manually
  - `--next-version` is not required anymore, it will be set by calculating the next `dev` version, if not manually set.
- The new Changelog and setting the next version is now done after the release within `pontos-release release` [#104](https://github.com/greenbone/pontos/pull/104)
- The parameter `--project` in pontos-release, it not required anymore and by default resolved by `get_project_name()` [#105](https://github.com/greenbone/pontos/pull/105)

### Removed

[21.6.0]: https://github.com/greenbone/pontos/compare/v21.4.0...v21.6.0

## [21.4.0] - 2021-04-20
### Changed
- Refactored release module and changed the arguments of release, prepare and
  sign commands [#80](https://github.com/greenbone/pontos/pull/80)

[21.4.0]: https://github.com/greenbone/pontos/compare/v21.3.0...v21.4.0

## [21.3.0] - 2021-03-31
### Changed
- Update dependencies to allow to use tomlkit >= 0.5.11 [#73](https://github.com/greenbone/pontos/pull/73)

[21.3.0]: https://github.com/greenbone/pontos/compare/v21.2.0...v21.3.0

## [21.2.0] - 2021-02-08

### Added
- New command called `pontos-update-header` to update years in copyright headers [#58](https://github.com/greenbone/pontos/pull/58)
- Tests for `pontos-update-header` added. [#59](https://github.com/greenbone/pontos/pull/59)[#60](https://github.com/greenbone/pontos/pull/60)

### Changed
- Renamed `pontos-copyright` to `pontos-update-header`. This tool now adds copyright header to files, if missing. [#59](https://github.com/greenbone/pontos/pull/59)
- Change versioning to [Calendar Versioning](https://calver.org)[#61](https://github.com/greenbone/pontos/pull/61)

[21.2.0]: https://github.com/greenbone/pontos/compare/v0.3.1...v21.2.0

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
