# typemap

PEP 827 type manipulation library for Python 3.14+

## Installation

```bash
pip install typemap
```

## Overview

typemap provides utilities for working with [PEP 827](https://peps.python.org/pep-0827/) type manipulation operators. It includes:

- **`eval_typing`** - Evaluate type expressions at runtime
- **Type operators** via `typemap_extensions`:
  - `Member` - Access type members by name
  - `Attrs` - Get class attributes
  - `Iter` - Iterate over type contents
  - `Param` - Define callable parameters
  - `UpdateClass` - Generate class modifications
  - `NewProtocol` - Create protocols dynamically
  - `IsAssignable` - Check type assignability
  - `KeyOf` - Get all member names as tuple of Literals
  - `Template` - Build template literal strings
  - `DeepPartial` - Make all fields recursively optional
  - `Partial` - Make all fields optional (non-recursive)
  - `Required` - Remove Optional from all fields
  - `Pick` - Pick specific fields from a type
  - `Omit` - Omit specific fields from a type

## Usage

### Evaluating Types

```python
from typemap import eval_typing

class MyClass:
    x: int
    y: str

result = eval_typing(MyClass)
print(result)
```

### Type Utilities

typemap provides several type utility operators for transforming types:

```python
from typing import Literal
import typemap_extensions as tm

# KeyOf - Get all member names as tuple of Literals
class User:
    name: str
    age: int

keys = tm.KeyOf[User]
# Result: tuple[Literal["name"], Literal["age"]]

# Partial - Make all fields optional (non-recursive)
PartialUser = tm.Partial[User]
# Result: class with name: str | None, age: int | None

# DeepPartial - Make all fields recursively optional
DeepUser = tm.DeepPartial[User]
# Result: class with all nested fields optional

# Required - Remove Optional from all fields
class OptionalUser:
    name: str | None
    age: int | None

RequiredUser = tm.Required[OptionalUser]
# Result: class with name: str, age: int

# Pick - Select specific fields
PublicUser = tm.Pick[User, tuple["name"]]
# Result: class with only name: str

# Omit - Exclude specific fields
SafeUser = tm.Omit[User, tuple["password"]]
# Result: class without password field
```

### Using UpdateClass

```python
from typing import Callable, Literal, Self, Never
import typemap_extensions as typing

type InitFn[T] = typing.Member[
    Literal["__init__"],
    Callable[
        [
            typing.Param[Literal["self"], Self],
            *[
                typing.Param[p.name, p.type]
                for p in typing.Iter[typing.Attrs[T]]
            ],
        ],
        None,
    ],
    Literal["ClassVar"],
]

class Model:
    def __init_subclass__[T](cls: type[T]) -> typing.UpdateClass[InitFn[T]]:
        super().__init_subclass__()

class User(Model):
    name: str
    age: int
```

## Development

```bash
# Install dependencies
cd packages/typemap
uv sync

# Run tests
uv run pytest

# Run type checking
uv run mypy src/typemap/

# Run linting
uv run ruff check src/typemap/
```

## Requirements

- Python 3.14+
- typing_extensions >= 4.0
