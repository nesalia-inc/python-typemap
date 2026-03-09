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

---

## About This Project

> **This project is 100% inspired by [vercel/python-typemap](https://github.com/vercel/python-typemap). All the credit and work goes to them - they are the real creators of this implementation.**

This repository is simply a **packaged version** of the original work by Vercel. The goal is to make this PEP 827 implementation available on PyPI for easier installation and distribution.

**All the intellectual work, research, and implementation was done by the Vercel team.** They are the ones who wrote the PEP draft, created the prototype, and demonstrated what's possible with type manipulation in Python.

We hope with all our hearts that [PEP 827](https://peps.python.org/pep-0827/) will be accepted. This PEP represents a major step forward for Python's type system and would enable powerful type-level computations that are currently only possible in TypeScript.

If you appreciate this work, please star and support the original [vercel/python-typemap](https://github.com/vercel/python-typemap) repository!
