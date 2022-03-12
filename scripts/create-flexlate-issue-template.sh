#!/bin/bash

if [ "$(git diff --stat HEAD~1 -- .github/workflows/)" ]; then
  echo "Updates to workflows detected.";
  echo ::set-output name=workflow_updated::true;
  issue_reason="the current updates include changes to the Github Actions workflow files, and Github Actions does not allow those to be updated by another workflow."
else
  echo "No updates to workflows.";
  echo ::set-output name=workflow_updated::false;
  issue_reason="there were merge conflicts while applying the update."
fi;

cat << EOF > temp-issue-template.md;
---
title: Manual Update to Files from Copier Needed
labels: automated issue, maintenance
---
The template from the [Copier that created this project][1] must be updated using Flexlate.

Normally this is an automated process, but $issue_reason

Run \`pipenv run fxt update -n\` then manually review and update the changes, before pushing a PR
for this.

```
fxt check
$(fxt check)
```

[1]: https://github.com/nickderobertis/copier-pypi-sphinx-flexlate

EOF