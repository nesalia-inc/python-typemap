# Features Documentation

This folder contains detailed documentation about TypeScript features and their PEP 827 / typemap equivalents.

Each document includes:
1. TypeScript feature explanation
2. PEP 827 current status
3. **Ideal DX Proposal (No Grammar Change)** - Practical DX using existing operators

---

## Available Documents

| Document | Description | Status |
|----------|-------------|--------|
| [infer.md](./infer.md) | Type inference with `infer` keyword | ✅ Testé - Fonctionne |
| [indexed_access.md](./indexed_access.md) | Indexed access types `T['key']` | ✅ Testé - Fonctionne |
| [template_literals.md](./template_literals.md) | Advanced template literal types | ✅ Testé - Fonctionne |
| [branding.md](./branding.md) | Type branding and widening | ✅ Testé - Fonctionne |
| [recursive_types.md](./recursive_types.md) | Recursive type definitions | ✅ Testé - Fonctionne (classes) |
| [this_type.md](./this_type.md) | ThisType utility and Self type | ✅ Testé - Fonctionne |

---

## Quick Reference

### Fully Supported ✅ (TESTED 2026-03-03)

- `Self` type (equivalent to TypeScript's `ThisType`)
- `GetArg` for type extraction (ReturnType, ParamTypes, ArrayElem, DictValue)
- `GetMemberType` for member access
- `KeyOf` for getting all member names
- `StrConcat`, `Uppercase`, `Lowercase`, `Capitalize` for string ops
- `NewProtocol` for branding
- Classes for recursive types

### Tested Helpers

All these helpers were tested and work:

```python
# infer.md helpers
type ReturnType[T] = GetArg[T, Callable, Literal[1]]
type ParamTypes[T] = GetArg[T, Callable, Literal[0]]
type FirstParam[T] = GetArg[GetArg[T, Callable, Literal[0]], tuple, Literal[0]]
type ArrayElem[T] = GetArg[T, list, Literal[0]]
type DictValue[T] = GetArg[T, dict, Literal[1]]

# indexed_access.md helpers
type MemberTypes[T] = NewProtocol[*[Member[p.name, p.type] for p in Iter[Attrs[T]]]]
type KeyOf[T]  # Already exists!
type NestedGet[T, K1, K2] = GetMemberType[GetMemberType[T, K1], K2]

# template_literals.md helpers
type Pluralize[S] = StrConcat[S, 's']
type RouteBuilder[R] = StrConcat['/', R]
type EventHandler[E] = StrConcat['on', Capitalize[E]]

# recursive_types.md
class LinkedList[T]:
    value: T
    next: LinkedList[T] | None = None

# branding.md
class Brand(Protocol):
    value: str

class UserId(Brand): pass
class OrderId(Brand): pass
```

### Available Workarounds (No Grammar Change)

- `infer` → Use `GetArg` - [infer.md](./infer.md#ideal-dx-proposal-no-grammar-change)
- Template literals → Use `StrConcat` - [template_literals.md](./template_literals.md#ideal-dx-proposal-no-grammar-change)
- Type branding → Use `NewProtocol` - [branding.md](./branding.md#ideal-dx-proposal-no-grammar-change)
- Recursive types → Use classes - [recursive_types.md](./recursive_types.md#ideal-dx-proposal-no-grammar-change)
- Mapped types → Use `Iter[Attrs[T]]` - [indexed_access.md](./indexed_access.md#ideal-dx-proposal-no-grammar-change)

---

## Key Principle

All "Ideal DX" proposals use **existing PEP 827 operators**:
- `GetMemberType`, `GetArg`
- `Iter`, `Attrs`, `Members`
- `NewProtocol`, `UpdateClass`
- `StrConcat`, `Uppercase`, `Lowercase`, `Capitalize`
- `IsAssignable`, `IsEquivalent`, `Bool`

---

## Related Documents

- [TypeScript Feature Comparison](../typescript_feature_comparison.md) - Complete comparison table
- [PEP 827 Analysis](../pep_select_function_analysis.md) - Deep dive into PEP examples
- [DX Levels](../developer_experience_levels.md) - Multi-level API design

---

*Last updated: 2026-03-03 (All features tested and verified)*
