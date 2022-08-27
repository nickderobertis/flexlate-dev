run := "mvenv run global --"
run-lint := "mvenv run lint --"
run-test := "mvenv run test --"
run-docs := "mvenv run docs --"

default:
    #!/usr/bin/env bash
    exit_code=0

    just format || ((exit_code++))
    just strip || ((exit_code++))
    just lint || ((exit_code++))
    just test || ((exit_code++))

    exit $exit_code

check:
    #!/usr/bin/env bash
    exit_code=0

    just format-check || ((exit_code++))
    just strip-check || ((exit_code++))
    just lint || ((exit_code++))
    just test || ((exit_code++))

    exit $exit_code


format *FILES='.':
    {{run}} isort {{FILES}}
    {{run}} black {{FILES}}

format-check *FILES='.':
    {{run}} isort --check-only {{FILES}}
    {{run}} black --check {{FILES}}

lint:
    {{run-lint}} flake8 --count --select=E9,F63,F7,F82 --show-source --statistics
    {{run-lint}} flake8 --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
    {{run-lint}} mypy

strip-opts := "--remove-all-unused-imports --in-place --recursive --exclude=test*,__init__.py,venv*,build*,dist*,node_modules*"

strip *FILES='.':
    {{run}} autoflake {{strip-opts}} {{FILES}}

strip-check *FILES='.':
    {{run}} autoflake --check {{strip-opts}} {{FILES}}

test *OPTIONS:
    {{run-test}} pytest {{OPTIONS}}

test-coverage *OPTIONS:
    {{run-test}} pytest --cov=./ --cov-report=xml {{OPTIONS}}

docs-build:
    cd docsrc && {{run-docs}} make github

docs-serve:
    cd docsrc && {{run-docs}} ./dev-server.sh

docs:
    just docs-build
    just docs-serve
