# Testing

## Usage

```
pip install tox
```

The following command runs the linter and all the unit tests for the selected versions of Python (py35, py36, py37, py38)

```
tox
```

And for an specific Python version

```
tox -e py37
```

## File structure

```
tests
├── e2e
└── unit
```

```
tox -e unit
tox -e e2e
```

## Framework

### Linter

We use `flake8` in CI because it's standard, fast and compatible with GitHub tools like Hound. However, we use also `pylint`for a deeper lint analysis with `tox -e lint`.

### Coverage

We use `pytest-cov` to compute the coverage of the tests. There are two commands available: `tox -e cov` which provides a simple console report, and `tox -e cov-html` which creates an HTML report in the `htmlcov` folder.

### Testing

We use `pytest` to run both the `unit` and `e2e` tests. This tool is fully compatible with the standard `unittest`, but we will try to avoid using unittest directly in the code.

Here we have some simple examples to show the basic structure of test in some situations:

**Basic test**

```py
def test_basic():
    [...]
    assert a == 1
    assert b == '...'
    assert c is True
    assert d is not None
```

**Exceptions**

```py
import pytest

def test_exceptions():
    with pytest.raises(ValueError) as e:
        [...]
    assert str(e.value) == '...'
```

**Fixtures**

```py
@pytest.fixture
def smtp_connection():
    import smtplib
    return smtplib.SMTP('smtp.gmail.com', 587, timeout=5)


def test_ehlo(smtp_connection):
    response, msg = smtp_connection.ehlo()
    assert response == 250
```

**Mocks**

```py
# Note: the mocker is injected by pytest as a fixture
def test_simple_mocking(mocker):
    mock_db_service = mocker.patch('other_code.services.db_service', autospec=True)
    mock_db_service.return_value = <value>
    mock_db_service.side_effect = <function>

    # Calling service with the mock
    count_service('foo')

    mock_db_service.assert_called_with('foo')
```

NOTE: avoid `assert_called_once` because it does not work in Python 3.5.

**Classes**

```py
class TestSomething(object):

    def setup_method(self):
        pass

    def teardown_method(self):
        pass

    def test_something(self):
        pass
```

**Skipping**

```py
@pytest.mark.skipif(condition, reason='...')
def function():
    pass
```

### Pre-commit (optional, but :sparkles:)

This tool runs the linter before any `git commit` :smile:.

**Installation**

```
pip install pre-commit
```

```
pre-commit install
```
