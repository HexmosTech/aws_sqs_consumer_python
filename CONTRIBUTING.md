# Contributing

## Development setup

**Install poetry**

We use [`poetry`](https://python-poetry.org/) for packaging and dependency management.

Refer [Poetry installation](https://python-poetry.org/docs/#installation)

```
poetry --version
```

**Install dependencies**

```
poetry install
```

## Making changes

### Tests

After making any changes, run the tests:

```
poetry shell
python -m unittest discover
```

## Documentation

**Build**

```
poetry shell
cd docs
make html
python -m http.server --directory _build/html 5001
```

Open [http://localhost:5001](http://localhost:5001) to see the local documentation site

### Linting

We use [`flake8`](https://flake8.pycqa.org/en/latest/) for linting. Ensure no linting errors:

```
poetry shell
python -m flake8 aws_sqs_consumer tests
```

## Manual publishing (authors only)

### Prerequisites (One time setup)

**API Token**

Create an API token with `Project: aws-sqs-consumer` scope, keep the generated token handy. Perform this step for both `test.pypi.org` and `pypi.org`:

* [https://test.pypi.org/manage/account/token/](https://test.pypi.org/manage/account/token/)
* [https://pypi.org/manage/account/token/](https://pypi.org/manage/account/token/)

**Configure poetry with `test.pypi.org`**

```
poetry config repositories.test-pypi https://test.pypi.org/legacy/
poetry config pypi-token.test-pypi <test_pypi_api_token>
```

**Configure poetry with `pypi.org`**

```
poetry config pypi-token.pypi <pypi_api_token>
```

### Build

Remember to change the version:

* Bump the version in [aws_sqs_consumer/__init__.py](aws_sqs_consumer/__init__.py)
* Bump the version in [pyproject.toml](pyproject.toml)

Go to the repository root, and run the following commands:

```
rm -rf dist
poetry build
```

This will create two files:

* `dist/aws_sqs_consumer-<version>-py3-none-any.whl`
* `dist/aws_sqs_consumer-<version>.tar.gz`

### Publish

**Publishing to `test.pypi.org`**

```
poetry publish -r test-pypi
```

**Publishing to `pypi.org`**

```
poetry publish
```