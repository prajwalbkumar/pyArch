# Guideline - Release Versioning

Semantic Versioning (SemVer) is a versioning scheme that helps you clearly communicate changes in your software. It follows a `MAJOR.MINOR.PATCH` format and is widely used in software development to manage version numbers systematically. Here’s a breakdown of how to use Semantic Versioning for your pyRevit tools:

#### Semantic Versioning Format

1. **MAJOR version**: Increment this when you make incompatible changes that break backward compatibility.
2. **MINOR version**: Increment this when you add functionality in a backward-compatible manner.
3. **PATCH version**: Increment this when you make backward-compatible bug fixes.

Optional suffixes can be used to denote pre-release or build metadata.

#### Example Versioning

* **1.0.0**: The first stable release of your tool.
* **1.1.0**: Adds new features in a backward-compatible way.
* **1.1.1**: Fixes a bug in version 1.1.0.
* **2.0.0**: Introduces changes that are not backward compatible.

***

#### Version Numbering Guidelines for pyArch Tools

1. **Initial Development**:
   * Use `0.x.x` for early development stages, where you might expect frequent changes and instability.
   * Example: `0.1.0` (initial development), `0.2.0` (major new features or significant changes).
2. **Stable Releases**:
   * Start with `1.0.0` once you are ready to release a stable version.
   * Use `1.x.x` for minor updates and bug fixes that are backward-compatible.
   * Example: `1.0.1` (minor bug fix), `1.1.0` (new features), `1.2.0` (more features or improvements).
3. **Pre-Releases**:
   * You can add a pre-release label to indicate versions that are not yet fully stable or feature complete.
   * Example: `1.0.0-alpha`, `1.0.0-beta`, `1.0.0-rc1` (where `rc` stands for "release candidate").
