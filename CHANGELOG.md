# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- Support for UNIX socket redis connections
- Generating redis configurations from a given URL

### Changed
- Minimum required version of `redis-py` is now `4.0`

### Removed
- Removed support for Python 3.7 and Python 3.8

### Fixed
- Individual concurrency locks expire despite connection errors

## [1.0.3] - 2022-01-19
### Changed
- Updated badges

## [1.0.2] - 2022-01-19
### Changed
- Updated repository URL

## [1.0.1] - 2021-11-13
### Fixed
- Fixed package name in README.md

## [1.0.0] - 2021-11-11
### Added
- Concurrency limit context-manager
- Support for creating and managing Redis connections
- Support for using existing Redis connection pools

[Unreleased]: https://github.com/anexia/python-concurrency-limit/compare/1.0.3...HEAD
[1.0.3]: https://github.com/anexia/python-concurrency-limit/compare/1.0.2...1.0.3
[1.0.2]: https://github.com/anexia/python-concurrency-limit/compare/1.0.1...1.0.2
[1.0.1]: https://github.com/anexia/python-concurrency-limit/compare/1.0.0...1.0.1
[1.0.0]: https://github.com/anexia/python-concurrency-limit/releases/tag/1.0.0
