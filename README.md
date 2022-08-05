

[![](https://codecov.io/gh/nickderobertis/flexlate-dev/branch/master/graph/badge.svg)](https://codecov.io/gh/nickderobertis/flexlate-dev)
[![PyPI](https://img.shields.io/pypi/v/flexlate-dev)](https://pypi.org/project/flexlate-dev/)
![PyPI - License](https://img.shields.io/pypi/l/flexlate-dev)
[![Documentation](https://img.shields.io/badge/documentation-pass-green)](https://nickderobertis.github.io/flexlate-dev/)
![Tests Run on Ubuntu Python Versions](https://img.shields.io/badge/Tests%20Ubuntu%2FPython-3.8%20%7C%203.9%20%7C%203.10-blue)
[![Github Repo](https://img.shields.io/badge/repo-github-informational)](https://github.com/nickderobertis/flexlate-dev/)


#  flexlate-dev

## Overview

Development tools for template authors using Flexlate

## Getting Started

Install `flexlate-dev`:

```
pip install flexlate-dev
```

A simple example:

```python
import flexlate_dev

# Do something with flexlate_dev
```

See a
[more in-depth tutorial here.](
https://nickderobertis.github.io/flexlate-dev/tutorial.html
)

## Development Status

This project is currently in early-stage development. There may be
breaking changes often. While the major version is 0, minor version
upgrades will often have breaking changes.

## Developing

First, you need a couple global dependencies installed, see their documentation for details:
- [pipx](https://pypa.github.io/pipx/installation/)
- [direnv](https://direnv.net/docs/installation.html)

Then clone the repo and run `npm install` and `mvenv sync dev`. Make your changes and then run `just` to run formatting,
linting, and tests.

Develop documentation by running `just docs` to start up a dev server.

To run tests only, run `just test`. You can pass additional arguments to pytest,
e.g. `just test -k test_something`.

Prior to committing, you can run `just` with no arguments to run all the checks.

## Author

Created by Nick DeRobertis. MIT License.

## Links

See the
[documentation here.](
https://nickderobertis.github.io/flexlate-dev/
)
