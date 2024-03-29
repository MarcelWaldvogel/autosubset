# Change Log
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/)
and this project adheres to [Semantic Versioning](https://semver.org/).


# 0.2.2 - 2023-04-01
## Added
- `--quiet` suppresses the HTML+CSS output

## Fixed

## Changed


# 0.2.1 - 2021-12-02
## Added
- Alias `--ascii` for `--ascii-printable`
- XHTML compatibility

## Fixed
- `<link>` tag now with correct `as="font"`

## Changed
- Output now groups HTML and CSS code separately
- Version numbers of non-tagged versions now end in `.postX`, where `X` is the
  number of commits since the tag (unless overridden by `FORCE_VERSION`
  environment variable).


# 0.2.0 - 2020-12-05
## Added
- Command line parsing
- Multiple font files
- Support for forcing digits, ASCII letters (a-z, A-Z), or the entire ASCII
  printable range to be included in the subset, even if the characters do not
  appear in the input

## Fixed

## Changed


# 0.1.0 - 2020-12-05
## Added
- Initial release

## Fixed

## Changed
