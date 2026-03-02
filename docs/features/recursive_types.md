# Recursive Types - TypeScript vs PEP 827

This document explains recursive types in TypeScript and their status in PEP 827.

---

## What are Recursive Types?

Recursive types are types that reference themselves in their definition. They're useful for representing tree-like structures, nested data, and self-referential types.

---

## TypeScript Recursive Types

### Basic Example: Linked List

```typescript
type LinkedList<T> = {
  value: T;
  next: LinkedList<T> | null;
};

// Usage
type IntList = LinkedList<number>;

const list: IntList = {
  value: 1,
  next: {
    value: 2,
    next: {
      value: 3,
      next: null,
    }
  }
};
```

### Tree Structure

```typescript
type TreeNode<T> = {
  value: T;
  children: TreeNode<T>[];
};

// Binary Tree
type BinaryTree<T> = {
  value: T;
  left: BinaryTree<T> | null;
  right: BinaryTree<T> | null;
};
```

### Nested Object

```typescript
type JSONValue =
  | string
  | number
  | boolean
  | null
  | JSONValue[]
  | { [key: string]: JSONValue };

// Recursive with constraints
type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};
```

### Complex: Expression Parser

```typescript
type Expression =
  | { type: 'literal'; value: string | number }
  | { type: 'binary'; op: '+' | '-' | '*' | '/'; left: Expression; right: Expression }
  | { type: 'unary'; op: '-' | '+'; argument: Expression }
  | { type: 'identifier'; name: string };

function evaluate(expr: Expression): number {
  switch (expr.type) {
    case 'literal': return expr.value as number;
    case 'binary':
      const l = evaluate(expr.left);
      const r = evaluate(expr.right);
      return eval(`${l} ${expr.op} ${r}`);
    case 'unary': return evaluate(expr.argument) * (expr.op === '-' ? -1 : 1);
    case 'identifier': return 0;
  }
}
```

---

## PEP 827 Status

### Can PEP 827 Handle Recursive Types?

**Partially** - PEP 827 supports recursive type aliases, but with limitations.

### Working Example

```python
# In Python/PEP 827, recursive types can work
# But need to use explicit Protocol or class definitions

class LinkedList[T]:
    value: T
    next: LinkedList[T] | None  # Recursive reference
```

### The Problem with Type Aliases

```python
# This might NOT work in PEP 827
type JSONValue = (
    str
    | int
    | bool
    | None
    | list[JSONValue]
    | dict[str, JSONValue]
)
```

The issue is that `JSONValue` references itself in the type alias, which can cause evaluation issues.

---

## Comparison Table

| TypeScript | PEP 827 | Notes |
|------------|---------|-------|
| `type List<T> = { next: List<T> }` | ⚠️ | Limited support |
| Recursive type aliases | ⚠️ | May cause evaluation issues |
| Self-referential classes | ✅ | Works in classes |
| Infinite types | ❌ | Not supported |

---

## Workarounds in PEP 827

### Using Classes Instead of Type Aliases

```python
# Define recursive types as classes
class LinkedList[T]:
    value: T
    next: LinkedList[T] | None = None
```

### Using Protocols for Structural Types

```python
from typing import Protocol

class JSONValue(Protocol):
    pass  # Define as needed
```

### Manual Expansion

```python
# Instead of recursive alias, define explicitly
class JSONValue:
    pass  # Not truly recursive
```

---

## Limitations in PEP 827

### 1. Type Alias Evaluation

Recursive type aliases can cause infinite loops during evaluation:

```python
# Could cause issues
type DeepList[T] = list[T | DeepList[T]]
```

### 2. No Self-Referencing in Type Aliases

```python
# This might not work
type Tree[T] = TreeNode[T] | None  # References itself
```

### 3. Protocol Limitations

```python
# Can't easily define recursive protocol
class Tree[T]:
    pass  # Needs explicit implementation
```

---

## Real-World Comparison

### JSON Type

```typescript
// TypeScript
type JSON =
  | string
  | number
  | boolean
  | null
  | JSON[]
  | { [key: string]: JSON };
```

```python
# PEP 827 - Not easily possible as alias
# Need to use class or accept limitations
```

### Deep Partial

```typescript
// TypeScript
type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P]
};
```

```python
# PEP 827 - Using Iter and Attrs
type DeepPartial[T] = NewProtocol[
    *[
        Member[
            p.name,
            p.type | None,  # Make optional
            p.quals,
        ]
        for p in Iter[Attrs[T]]
    ]
]
# Note: Not truly recursive
```

---

## Summary

| Feature | TypeScript | PEP 827 |
|---------|-----------|---------|
| Basic recursion | ✅ | ⚠️ |
| Type alias recursion | ✅ | ⚠️ Limited |
| Class recursion | ✅ | ✅ |
| Infinite types | ✅ | ❌ |
| Mutual recursion | ✅ | ❌ |

---

## Recommendations

1. **Use classes** for recursive types in PEP 827
2. **Avoid recursive type aliases** if possible
3. **Manual expansion** when needed
4. **Accept limitations** of the type system

---

## Ideal DX Proposal (No Grammar Change)

### Goal: Use classes for recursion

Use Python classes instead of type aliases for recursive definitions.

### What We Can Build Today

```python
# 1. Recursive classes (works!)
class LinkedList[T]:
    value: T
    next: LinkedList[T] | None = None

# Usage
type IntList = LinkedList[int]
# Has: value: int, next: LinkedList[int] | None

# 2. Tree structure
class TreeNode[T]:
    value: T
    children: list[TreeNode[T]] = []

# 3. JSON-like structure using classes
class JSONValue:
    pass  # Base type

class JSONString(JSONValue):
    value: str

class JSONNumber(JSONValue):
    value: int | float

class JSONArray(JSONValue):
    items: list[JSONValue]

class JSONObject(JSONValue):
    fields: dict[str, JSONValue]

# Type union
type JSON = JSONString | JSONNumber | JSONArray | JSONObject | None
```

### For Type-Level Deep Operations

```python
# Instead of recursive type alias, use explicit depth

# Depth-limited types
type DeepPartial1[T] = NewProtocol[
    *[
        Member[p.name, p.type | None, p.quals]
        for p in Iter[Attrs[T]]
    ]
]

# For nested, compose explicitly
type DeepPartial2[T] = NewProtocol[
    *[
        Member[
            p.name,
            DeepPartial1[p.type] if IsAssignable[p.type, object] else p.type | None,
            p.quals,
        ]
        for p in Iter[Attrs[T]]
    ]
]

# This is verbose but works with current syntax
```

### Practical DX Pattern

```python
# Create recursive types using classes
class Recursive[T]:
    """Base for recursive types"""
    pass

class Node[T](Recursive[T]):
    value: T
    children: list[Recursive[T]]

# Usage
type StringTree = Node[str]
# Has: value: str, children: list[Node[str]>
```

### Summary

| Approach | Works Today | Notes |
|----------|-------------|-------|
| Classes with self-reference | ✅ | Use this! |
| Type alias recursion | ⚠️ | May cause issues |
| Max depth manually | ✅ | Verbose but safe |
| Protocol-based | ✅ | Clean approach |

**Recommendation:** Use **classes** for recursive types in PEP 827.

---

## References

- [TypeScript Recursive Types](https://www.typescriptlang.org/docs/handbook/2/types-from-types.html#recursive-type-aliases)

---

*Last updated: 2026-03-02*
