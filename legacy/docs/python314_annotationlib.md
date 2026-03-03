# Python 3.14 annotationlib and typemap

This document describes the relationship between Python 3.14's new `annotationlib` module and the typemap project.

---

## Overview

Python 3.14 introduces `annotationlib` (PEP 649, PEP 749), which provides tools for introspecting lazily evaluated annotations. This is directly relevant to typemap's goals.

---

## annotationlib Features

### Get Annotations with Different Formats

```python
from annotationlib import get_annotations, Format

def func(arg: Undefined):
    pass

# VALUE: evaluates immediately (like old behavior)
get_annotations(func, format=Format.VALUE)
# Raises NameError if 'Undefined' is not defined

# FORWARDREF: returns ForwardRef for unresolved names
get_annotations(func, format=Format.FORWARDREF)
# {'arg': ForwardRef('Undefined', owner=<function func>)}

# STRING: returns as source strings
get_annotations(func, format=Format.STRING)
# {'arg': 'Undefined'}
```

### Call Evaluate Functions

```python
from annotationlib import call_evaluate_function, Format
import typing

# Evaluate TypeAliasType
type Alias = undefined
call_evaluate_function(Alias.evaluate_value, Format.VALUE)
# Raises NameError

call_evaluate_function(Alias.evaluate_value, Format.FORWARDREF)
# ForwardRef('undefined')

call_evaluate_function(Alias.evaluate_value, Format.STRING)
# 'undefined'

# Evaluate TypeVar bound
T = TypeVar('T', bound=list)
call_evaluate_function(T.evaluate_bound, Format.VALUE)
# <class 'list'>
```

### Metaclass Integration

```python
import annotationlib
import typing

class ClassVarSeparator(type):
    def __new__(mcls, name, bases, ns):
        # Get annotate function before class is fully created
        if annotate := annotationlib.get_annotate_from_class_namespace(ns):
            annotations = annotationlib.call_annotate_function(
                annotate, format=annotationlib.Format.FORWARDREF
            )
            # Process annotations...
        return super().__new__(mcls, name, bases, ns)
```

---

## Comparison with typemap

### What annotationlib Provides

| Feature | annotationlib | typemap | Notes |
|---------|---------------|---------|-------|
| Get annotations | `get_annotations()` | Custom implementation | annotationlib is more robust |
| ForwardRef handling | Native | Partial | annotationlib is better |
| TypeAlias evaluation | `call_evaluate_function()` | Custom | annotationlib is better |
| TypeVar bounds | `TypeVar.evaluate_bound()` | Missing | annotationlib has it |
| TypeVar constraints | `TypeVar.evaluate_constraints()` | Missing | annotationlib has it |
| ParamSpec defaults | `ParamSpec.evaluate_default()` | Missing | annotationlib has it |
| TypeVarTuple defaults | `TypeVarTuple.evaluate_default()` | Missing | annotationlib has it |

### What typemap Provides (that annotationlib doesn't)

| Feature | typemap | annotationlib | Notes |
|---------|---------|--------------|-------|
| Conditional types | Yes | No | Not in annotationlib |
| Type introspection | Yes | No | Member, Attrs, etc. |
| Type construction | Yes | No | NewProtocol, UpdateClass |
| Runtime type evaluation | Yes | No | Full typeEval |
| Type equality | Yes | No | Not in annotationlib |

---

## Integration Opportunities

### Option 1: Use annotationlib as Backend (Python 3.14+)

For Python 3.14+, typemap could use `annotationlib` for basic annotation retrieval:

```python
import sys

if sys.version_info >= (3, 14):
    from annotationlib import get_annotations, Format
    # Use annotationlib for annotation retrieval
else:
    # Use custom implementation
    from typemap.type_eval import eval_annotations
```

### Option 2: Extend with TypeVar Support

Add support for TypeVar bounds, constraints, and defaults:

```python
from typing import TypeVar, ParamSpec

T = TypeVar('T', bound=list)
T.evaluate_bound()  # Python 3.14+ only via annotationlib

# Could be used in typemap for:
# - Checking if a TypeVar has a bound
# - Extracting default values
# - Type constraint inference
```

### Option 3: Handle Forward References Better

```python
# Current typemap: needs custom handling
from typemap.type_eval import eval_typing

# Python 3.14+: could use annotationlib
from annotationlib import get_annotations, Format

# ForwardRef handling
def resolve_forward_ref(obj, forward_ref):
    return forward_ref.evaluate(
        owner=obj,
        globals=obj.__globals__,
        locals=getattr(obj, '__locals__', None)
    )
```

---

## Limitations

### annotationlib Doesn't Provide

1. **Type-level computation** - No conditional types, mapped types
2. **Type construction** - No NewProtocol, UpdateClass
3. **Type equality** - No structural type comparison
4. **Runtime evaluation** - Only retrieves annotations, doesn't evaluate complex types

### Security Considerations

From the documentation:

> Much of the functionality in this module involves executing code related to annotations, which can then do arbitrary things.

This applies to typemap as well - both require code execution.

---

## Recommendations

### Short Term

1. **Use annotationlib** for Python 3.14+ as a fallback for annotation retrieval
2. **Leverage** `call_evaluate_function` for TypeAliasType, TypeVar evaluation

### Long Term

1. **Investigate** integrating annotationlib's forward reference handling
2. **Document** the boundary between annotationlib and typemap
3. **Consider** making typemap work with both annotationlib (3.14+) and legacy (3.13-)

---

## References

- [PEP 649 - Deferred Evaluation of Annotations](https://peps.python.org/pep-0649/)
- [PEP 749 - Implementing PEP 649](https://peps.python.org/pep-0749/)
- [annotationlib documentation](https://docs.python.org/3.14/library/annotationlib.html)
- [Annotations Best Practices](https://docs.python.org/3.14/howto/annotations.html)

---

## Additional Python 3.14 Features

### inspect Module Updates

Python 3.14 updates the `inspect` module with several relevant changes:

#### signature() with annotation_format

```python
from inspect import signature
import annotationlib

# New in Python 3.14: control annotation format
sig = signature(foo, annotation_format=annotationlib.Format.STRING)
# Returns annotations as strings
```

#### get_annotations() is now an alias

```python
from inspect import get_annotations

# Now an alias for annotationlib.get_annotations()
get_annotations(func, format=annotationlib.Format.FORWARDREF)
```

#### getmembers_static() (Python 3.11+)

```python
from inspect import getmembers_static

# Get members without triggering descriptor protocol
getmembers_static(obj)
```

#### getattr_static()

```python
from inspect import getattr_static

# Introspect without executing __getattr__ or descriptors
getattr_static(obj, 'attr')
```

### ast Module Updates

Python 3.14 adds new AST nodes for template strings:

#### ast.TemplateStr (New in 3.14)

```python
import ast

# Template string AST representation
code = ast.parse('t"{name} finished {place:ordinal}"', mode='eval')
print(ast.dump(code, indent=2))
# Expression(
#   body=TemplateStr(
#     values=[
#       Interpolation(...),
#       Constant(...),
#       Interpolation(...)]))
```

#### ast.Interpolation (New in 3.14)

```python
# Represents a single interpolation in a template string
ast.Interpolation(
    value=Name(id='name', ctx=Load()),
    str='name',  # The source text of the interpolation
    conversion=-1  # No conversion
)
```

#### ast.compare() (New in 3.14)

```python
import ast

# Compare two ASTs
tree1 = ast.parse('x + y')
tree2 = ast.parse('x + y')
tree3 = ast.parse('x + z')

ast.compare(tree1, tree2)  # True
ast.compare(tree1, tree3)  # False

# Compare with attribute details
ast.compare(tree1, tree2, compare_attributes=True)  # Includes line numbers, etc.
```

---

## Integration Summary for typemap

| Module | Python 3.14 Feature | typemap Relevance |
|--------|---------------------|-------------------|
| annotationlib | `get_annotations()` | ✅ Use as backend |
| annotationlib | `call_evaluate_function()` | ✅ TypeVar/ParamSpec eval |
| inspect | `signature(annotation_format=)` | ✅ Control annotation format |
| inspect | `get_annotations()` alias | ✅ Simplifies code |
| ast | `TemplateStr` | Potential for future string types |
| ast | `Interpolation` | Template string parsing |
| ast | `compare()` | Type comparison utilities |

---

*Last updated: 2026-03-02*
