# Documentation Index

This file provides an overview of all documentation in this project.

---

## Getting Started

| Document | Description |
|----------|-------------|
| [README](../README.md) | Main project readme |
| [testing_types.md](testing_types.md) | How to test types |

---

## Specification

| Document | Description |
|----------|-------------|
| [pep.rst](../pep.rst) | PEP 827 - Type Manipulation (Full specification) |

---

## Feature Comparisons

| Document | Description |
|----------|-------------|
| [typescript_feature_comparison.md](typescript_feature_comparison.md) | TypeScript vs PEP 827 feature matrix |

### Feature Details

| Document | Description |
|----------|-------------|
| [features/infer.md](features/infer.md) | TypeScript `infer` vs PEP 827 `GetArg` |
| [features/indexed_access.md](features/indexed_access.md) | Indexed access types |
| [features/template_literals.md](features/template_literals.md) | String manipulation |
| [features/branding.md](features/branding.md) | Type branding |
| [features/recursive_types.md](features/recursive_types.md) | Recursive types |
| [features/this_type.md](features/this_type.md) | Self/ThisType |

---

## Developer Experience

| Document | Description |
|----------|-------------|
| [developer_experience_levels.md](developer_experience_levels.md) | DX proposal with 3 levels |
| [developer_experience.md](developer_experience.md) | General DX discussion |

---

## Deep Dives

| Document | Description |
|----------|-------------|
| [pep_select_function_analysis.md](pep_select_function_analysis.md) | Prisma-style ORM select() |
| [pep_dataclass_method_generation.md](pep_dataclass_method_generation.md) | Dataclass method generation |

---

## Implementation

| Document | Description |
|----------|-------------|
| [implementation_analysis.md](implementation_analysis.md) | What's tested, what's unknown |
| [helpers_testing_strategy.md](helpers_testing_strategy.md) | How to test new helpers |
| [package_development_plan.md](package_development_plan.md) | Plan to create package |

---

## Quick Links

### What's Working

- `Attrs[T]`, `Members[T]`, `Iter[T]`
- `NewProtocol[*Ms]`, `UpdateClass[*Ms]`
- `IsAssignable`, `IsEquivalent`, `Bool`
- `GetMemberType[T, K]`, `GetArg[T, B, I]`
- `StrConcat`, `Uppercase`, `Lowercase`, `Capitalize`

### Tested Helpers

- `Public[T]`, `Create[T]`, `Update[T]`, `AddInit[T]`
- `Pick[T, K]` - Filter by key name
- `Omit[T, K]` - Exclude by key name
- `Partial[T]` - Make all fields optional
- `DeepPartial[T]` - Nested optional (requires explicit recursion)

---

*Last updated: 2026-03-03*
