# fetch-github-issues

[![PyPI](https://img.shields.io/pypi/v/fetch-github-issues.svg)](https://pypi.org/project/fetch-github-issues/)
[![Changelog](https://img.shields.io/github/v/release/simonw/fetch-github-issues?include_prereleases&label=changelog)](https://github.com/simonw/fetch-github-issues/releases)
[![Tests](https://github.com/simonw/fetch-github-issues/actions/workflows/test.yml/badge.svg)](https://github.com/simonw/fetch-github-issues/actions/workflows/test.yml)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/simonw/fetch-github-issues/blob/master/LICENSE)

Fetch all GitHub issues for a repository

## Installation

Install this tool using `pip`:
```bash
pip install fetch-github-issues
```
## Usage

For help, run:
```bash
fetch-github-issues --help
```
You can also use:
```bash
python -m fetch_github_issues --help
```
## Development

To contribute to this tool, first checkout the code. Then create a new virtual environment:
```bash
cd fetch-github-issues
python -m venv venv
source venv/bin/activate
```
Now install the dependencies and test dependencies:
```bash
pip install -e '.[test]'
```
To run the tests:
```bash
pytest
```
