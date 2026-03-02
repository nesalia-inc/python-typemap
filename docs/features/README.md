# Features Documentation

This folder contains detailed documentation about TypeScript features and their PEP 827 / typemap equivalents.

Each document includes:
1. TypeScript feature explanation
2. PEP 827 current status
3. **Ideal DX Proposal (No Grammar Change)** - Practical DX using existing operators

---

## Available Documents

| Document | Description | DX Works With |
|----------|-------------|---------------|
| [infer.md](./infer.md) | Type inference with `infer` keyword | ✅ GetArg |
| [indexed_access.md](./indexed_access.md) | Indexed access types `T['key']` | ✅ GetMemberType |
| [template_literals.md](./template_literals.md) | Advanced template literal types | ✅ StrConcat, Uppercase |
| [branding.md](./branding.md) | Type branding and widening | ✅ NewProtocol |
| [recursive_types.md](./recursive_types.md) | Recursive type definitions | ✅ Classes |
| [this_type.md](./this_type.md) | ThisType utility and Self type | ✅ Already supported |

---

## Quick Reference

### Fully Supported ✅

- `Self` type (equivalent to TypeScript's `ThisType`)

### Partially Supported ⚠️

- Conditional types (`if/else` with `IsAssignable`)
- Mapped types (via `Iter[Attrs[T]]`)
- Indexed access (via `GetMemberType`)

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

*Last updated: 2026-03-02*
