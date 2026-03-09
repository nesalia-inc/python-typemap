# python-typemap

[![PyPI Version](https://img.shields.io/pypi/v/typemap)](https://pypi.org/project/typemap/)
[![Python Version](https://img.shields.io/python/py-version/typemap)](https://pypi.org/project/typemap/)
[![Test Status](https://github.com/nesalia-inc/python-typemap/actions/workflows/test.yml/badge.svg)](https://github.com/nesalia-inc/python-typemap/actions)
[![Codecov](https://codecov.io/gh/nesalia-inc/python-typemap/branch/main/graph/badge.svg)](https://codecov.io/gh/nesalia-inc/python-typemap)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

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
