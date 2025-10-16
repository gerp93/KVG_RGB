# Changelog

All notable changes to KVG RGB Controller will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Nothing yet

### Changed
- Nothing yet

### Fixed
- Nothing yet

## [0.1.0] - 2025-10-15

### Added
- Initial release
- CLI interface with subcommands (list, color, rainbow, breathe)
- Core RGBController class for programmatic control
- Support for controlling individual devices or all devices
- Rainbow effect with customizable speed and duration
- Breathing effect with customizable color, speed, and duration
- Standalone executable build system
- Python package distribution support

### Features
- List all connected RGB devices
- Set colors on devices
- Apply effects to specific devices or all devices
- Command-line interface with help documentation
- Reusable core library for future GUI development

---

## How to Update This File

When releasing a new version:

1. Move items from `[Unreleased]` to a new version section
2. Update the version number and date
3. Categorize changes as Added/Changed/Fixed/Removed
4. Keep `[Unreleased]` section at the top for ongoing work

Example:
```markdown
## [Unreleased]

### Added
- New pulse effect

## [0.2.0] - 2025-10-20

### Added
- Zone-specific color control
- Save/load color profiles

### Fixed
- Fixed connection timeout issue
```
