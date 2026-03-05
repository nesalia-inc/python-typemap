# Changelog

All notable changes to this project will be documented in this file.

## [0.2.0] - 2026-03-05

### Added

- **KeyOf[T]** - Returns all member names as a tuple of Literal types
  - Similar to TypeScript's `keyof` operator
  - Example: `KeyOf[User]` returns `tuple[Literal["name"], Literal["age"]]`

- **Template[*Parts]** - Template literal string builder
  - Concatenates string literal types at runtime
  - Example: `Template["api/v1/", Literal["users"]]` returns `Literal["api/v1/users"]`

- **DeepPartial[T]** - Make all fields recursively optional
  - Applies optional transformation to all nested types
  - Example: `DeepPartial[User]` makes all nested fields optional

- **Partial[T]** - Make all fields optional (non-recursive)
  - Makes all top-level fields optional without recursion
  - Example: `Partial[User]` returns `name: str | None, age: int | None`

- **Required[T]** - Remove Optional from all fields
  - Inverse operation of Partial
  - Example: `Required[OptionalUser]` removes `| None` from all fields

- **Pick[T, K]** - Pick specific fields from a type
  - Creates a new type with only the specified fields
  - Example: `Pick[User, tuple["name", "email"]]`

- **Omit[T, K]** - Omit specific fields from a type
  - Creates a new type excluding specified fields
  - Example: `Omit[User, tuple["password"]]`

### Changed

- Updated `typemap_extensions` to export all new type utilities

## [0.1.2] - 2026-03-04

### Added

- Initial release with core type evaluation
- Support for PEP 827 type manipulation
- `eval_typing` function for runtime type evaluation
- Core type operators: Member, Attrs, Iter, Param, UpdateClass, NewProtocol, IsAssignable
