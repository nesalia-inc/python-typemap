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
