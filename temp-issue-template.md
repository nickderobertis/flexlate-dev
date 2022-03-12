---
title: Manual Update to Files from Copier Needed
labels: automated issue, maintenance
---
The template from the [Copier which created this project][1] must be updated using Flexlate.

Normally this is an automated process, but there were merge conflicts while applying the update.

Run `pipenv run fxt update -n` then manually review and update the changes, before pushing a PR
for this.

[1]: https://github.com/nickderobertis/copier-pypi-sphinx-flexlate

