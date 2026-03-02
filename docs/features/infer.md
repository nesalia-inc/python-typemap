# The `infer` Keyword - TypeScript vs PEP 827

This document explains the `infer` keyword in TypeScript and why it's not available in PEP 827 (typemap).

---

## What is `infer`?

The `infer` keyword in TypeScript allows **type inference within conditional types**. It lets you extract and capture a type from another type.

---

## TypeScript `infer` Examples

### Extract Return Type

```typescript
type ReturnType<T> = T extends (...args: any[]) => infer R ? R : never;

// Usage
type Fn = (x: number) => string;
type R = ReturnType<Fn>;  // → string
```

### Extract Parameter Type

```typescript
type Parameters<T> = T extends (...args: infer P) => any ? P : never;

// Usage
type Fn = (x: number, y: string) => void;
type Params = Parameters<Fn>;  → [number, string]
```

### Extract Array Element

```typescript
type ArrayElement<T> = T extends (infer E)[] ? E : never;

// Usage
type Arr = string[];
type Elem = ArrayElement<Arr>;  // → string
```

### Nested Inference

```typescript
type Flatten<T> = T extends Array<infer U> ? U : T;

// Usage
type Nested = string[][];
type Flat = Flatten<Nested>;  // → string[]
```

---

## PEP 827 Equivalent

PEP 827 does **NOT** have the `infer` keyword. Instead, it uses explicit operators:

### Extract Return Type

```python
# TypeScript
type ReturnType<T> = T extends (...args: infer R) => infer P ? P : never

# PEP 827 - Explicit GetArg
type ReturnType[T] = GetArg[T, Callable, Literal[1]]
# Returns the 2nd type argument (index 1) which is the return type
```

### Extract Parameter Types

```python
# TypeScript
type Parameters<T> = T extends (...args: infer P) => any ? P : never

# PEP 827 - More complex
# Need to extract from Callable params
```

### Extract Array Element

```python
# TypeScript
type ArrayElement<T> = T extends (infer E)[] ? E : never

# PEP 827 - Explicit GetArg
type ArrayElement[T] = GetArg[T, list, Literal[0]]
# Get the first type argument of list
```

---

## Comparison Table

| TypeScript | PEP 827 (typemap) | Notes |
|------------|-------------------|-------|
| `infer R` in return | `GetArg[T, Callable, 1]` | Explicit index |
| `infer P` in params | Complex extraction | No direct equivalent |
| `infer E` in array | `GetArg[T, list, 0]` | Explicit type argument |
| Nested inference | Multiple GetArg | Manual composition |

---

## Why No `infer` in PEP 827?

### 1. Syntax Limitations

The PEP explicitly mentions this limitation:

> *"Unfortunately it seems very difficult to shoehorn into Python's existing syntax in any sort of satisfactory way, especially because of the subtle binding structure."*

### 2. Runtime Evaluation

`infer` requires pattern matching that would be very difficult to implement in a runtime evaluator. Python's syntax doesn't naturally support:
- Capturing a type variable within an expression
- Back-referencing the captured variable elsewhere

### 3. Alternative Approaches

PEP 827 suggests alternatives:

```python
# TypeScript
type ArrayArg<T> = T extends [infer El] ? El : never

# PEP 827 alternative
type ArrayArg[T] = El if IsAssignable[T, list[Infer[El]]] else Never
```

But this requires a custom `Infer` mechanism that would need special handling.

---

## Workarounds in PEP 827

### 1. Using GetArg

For generic types with known structure:

```python
# Extract from a known generic
type FirstParam[T] = GetArg[T, Callable, Literal[0]]

# For a specific Callable
# Callable[[int, str], bool] → [int, str] is at index 0
```

### 2. Using Member Access

For class members:

```python
# Get member type
GetMemberType[Class, 'attribute_name']

# Get specific member
GetMember[Class, 'method_name']
```

### 3. Manual Composition

```python
# Build complex extractions manually
type ExtractReturn[T] = GetArg[
    GetArg[T, Callable, Literal[0]],  # First get the params
    tuple,
    Literal[0],  # Then get first param type
]
```

---

## Example: Recreating TypeScript Utilities

### Partial<T>

```python
# TypeScript
type Partial<T> = { [P in keyof T]?: T[P] }

# PEP 827 - Using Iter and Attrs
type Partial[T] = NewProtocol[
    *[
        Member[p.name, p.type | None, p.quals]
        for p in Iter[Attrs[T]]
    ]
]
```

### Pick<T, K>

```python
# TypeScript
type Pick<T, K extends keyof T> = { [P in K]: T[P] }

# PEP 827 - Need key filtering (not directly supported)
# Would require custom implementation
```

### ReturnType<T>

```python
# TypeScript
type ReturnType<T> = T extends (...args: any[]) => infer R ? R : any

# PEP 827
type ReturnType[T] = GetArg[T, Callable, Literal[1]]
```

### Parameters<T>

```python
# TypeScript
type Parameters<T> = T extends (...args: infer P) => any ? P : never

# PEP 827 - Complex, requires unpacking Callable params
# Not directly supported
```

---

## Missing Features Summary

| TypeScript Feature | PEP 827 Status |
|-------------------|-----------------|
| `infer` keyword | ❌ Not supported |
| `infer` in return position | ⚠️ Use `GetArg` |
| `infer` in parameter position | ❌ Not supported |
| Pattern matching in types | ❌ Not supported |

---

## Ideal DX Proposal (New Operators Allowed)

### Goal: Make type extraction ergonomic

Create helper classes that wrap `GetArg` for common patterns.

### Proposed New Operators

```python
# New helper class - uses GetArg internally
class ReturnType[T]:
    """Extract return type from a Callable"""
    # Implementation uses GetArg[T, Callable, Literal[1]]
    pass

class ParamTypes[T]:
    """Extract parameter types as tuple"""
    # Implementation uses GetArg[T, Callable, Literal[0]]
    pass

class FirstParam[T]:
    """Extract first parameter type"""
    # Implementation uses GetArg[GetArg[T, Callable, Literal[0]], tuple, Literal[0]]
    pass

class LastParam[T]:
    """Extract last parameter type"""
    # Implementation uses Length + GetArg
    pass

class ArrayElem[T]:
    """Extract element type from list[T]"""
    # Implementation uses GetArg[T, list, Literal[0]]
    pass

class DictValue[T]:
    """Extract value type from dict[K, V]"""
    # Implementation uses GetArg[T, dict, Literal[1]]
    pass
```

### Usage with Current Syntax

```python
# With these helpers:
type R = ReturnType[Callable[[int], str]]          # → str
type Params = ParamTypes[Callable[[int, str], bool]]  # → tuple[int, str]
type First = FirstParam[Callable[[int, str], bool]]  # → int
type Elem = ArrayElem[list[str]]                  # → str
type V = DictValue[dict[str, int]]                 # → int
```

### Implementation

```python
# These can be implemented TODAY with existing operators!
# Just wrap GetArg in a convenient class

type ReturnType[T] = GetArg[T, Callable, Literal[1]]
type ParamTypes[T] = GetArg[T, Callable, Literal[0]]
type ArrayElem[T] = GetArg[T, list, Literal[0]]
type DictValue[T] = GetArg[T, dict, Literal[1]]
```

### More Advanced Helpers

```python
# Extract all but first param
class RestParams[T] = Slice[
    GetArg[T, Callable, Literal[0]],
    Literal[1],
    None,
]

# Extract return and params
class FuncSignature[T] = tuple[
    GetArg[T, Callable, Literal[1]],  # Return
    GetArg[T, Callable, Literal[0]],  # Params
]
```
| Recursive type inference | ⚠️ Manual only |

---

## Recommendations

1. **For extracting type arguments**: Use `GetArg[T, Base, Index]`
2. **For class members**: Use `GetMemberType[T, 'name']`
3. **For complex inference**: Build custom type aliases with explicit operators
4. **For runtime flexibility**: Use the runtime evaluator with custom logic

---

## References

- [TypeScript Handbook - infer](https://www.typescriptlang.org/docs/handbook/2/conditional-types.html#infer)
- PEP 827 - Type Manipulation (Section: Rejected Ideas)

---

*Last updated: 2026-03-02*
