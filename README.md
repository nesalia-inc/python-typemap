# python-typemap

PEP 827 type manipulation library for Python 3.14+

## Installation

```bash
pip install typemap
```

## Overview

This repository contains the **typemap** package, which provides utilities for working with [PEP 827](https://peps.python.org/pep-0827/) type manipulation operators.

### Features

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

## Documentation

See [`packages/typemap/README.md`](packages/typemap/README.md) for detailed usage.

## Requirements

- Python 3.14+
- typing_extensions >= 4.0
