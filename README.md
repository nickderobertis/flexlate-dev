[![](https://codecov.io/gh/nickderobertis/flexlate-dev/branch/master/graph/badge.svg)](https://codecov.io/gh/nickderobertis/flexlate-dev)
[![PyPI](https://img.shields.io/pypi/v/flexlate-dev)](https://pypi.org/project/flexlate-dev/)
![PyPI - License](https://img.shields.io/pypi/l/flexlate-dev)
[![Documentation](https://img.shields.io/badge/documentation-pass-green)](https://nickderobertis.github.io/flexlate-dev/)
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

First ensure that you have `pipx` installed, if not, install it with `pip install pipx`.

Then clone the repo and run `npm install` and `pipenv sync`. Run `pipenv shell`
to use the virtual environment. Make your changes and then run `nox` to run formatting,
linting, and tests.

Develop documentation by running `nox -s docs` to start up a dev server.

## Author

Created by Nick DeRobertis. MIT License.

## Links

See the
[documentation here.](
https://nickderobertis.github.io/flexlate-dev/
)
