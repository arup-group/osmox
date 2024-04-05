<!---
Changelog headings can be any of:

Added: for new features.
Changed: for changes in existing functionality.
Deprecated: for soon-to-be removed features.
Removed: for now removed features.
Fixed: for any bug fixes.
Security: in case of vulnerabilities.

Release headings should be of the form:
## [X.Y.Z] - YEAR-MONTH-DAY
-->

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- Recommended installation instructions changed from using `pip` to creating a `mamba` environment [#38](https://github.com/arup-group/osmox/pull/38).
- Supported and tested Python versions updated to py3.10 - py3.12 [#38](https://github.com/arup-group/osmox/pull/38).
- Majority of documentation moved from README to dedicated documentation site: https://arup-group.github.io/osmox [#40](https://github.com/arup-group/osmox/pull/40).
- Default output format changed from `.geojson` to `.gpkg` & support for multiple file formats (`.gpkg`, `.geojson`, `.parquet`) [#41](https://github.com/arup-group/osmox/issues/41)

### Added

- Activity infilling can use a geospatial point data source to fill OSM `landuse` areas, e.g. postcode data points.

## [v0.2.0]

### Added

- Support for Python 3.11 by @val-ismaili in https://github.com/arup-group/osmox/pull/35
- A formal changelog

## [v0.1.0]

## Initial release

This is the first release and support Python 3.7, please check documentation/wiki for the usage guide