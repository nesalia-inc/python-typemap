"""Tests for PropsOnly type operator."""

import textwrap

from typing import Literal

from typemap.type_eval import eval_typing
import typemap_extensions as typing

from . import format_helper


# Define ORM-like types
class Pointer[T]:
    """Base pointer type."""
    pass


class Property[T](Pointer[T]):
    """Property type for scalar fields."""
    pass


class Link[T](Pointer[T]):
    """Link type for one-to-one relationships."""
    pass


class MultiLink[T](Link[T]):
    """MultiLink type for one-to-many relationships."""
    pass


# Test models
class User:
    id: Property[int]
    name: Property[str]
    email: Property[str]
    posts: MultiLink["Post"]  # relation, not a property
    profile: Link["Profile"]  # relation, not a property


class Post:
    id: Property[int]
    title: Property[str]
    content: Property[str]
    author: Link[User]  # relation


class Profile:
    id: Property[int]
    bio: Property[str]


class EmptyClass:
    """Class with no attributes."""
    pass


def test_propsonly_with_mixed_fields():
    """PropsOnly should extract only Property fields."""
    result = eval_typing(typing.PropsOnly[User])

    # Should have id, name, email but not posts or profile
    fmt = format_helper.format_class(result)

    # Check that we have the properties
    assert "id: int" in fmt
    assert "name: str" in fmt
    assert "email: str" in fmt

    # Relations should NOT be present
    assert "posts:" not in fmt
    assert "profile:" not in fmt


def test_propsonly_all_properties():
    """PropsOnly should work when all fields are Properties."""
    result = eval_typing(typing.PropsOnly[Post])

    fmt = format_helper.format_class(result)

    assert "id: int" in fmt
    assert "title: str" in fmt
    assert "content: str" in fmt


def test_propsonly_all_relations():
    """PropsOnly should return empty/minimal when all fields are relations."""
    class AllRelations:
        posts: MultiLink[Post]
        profile: Link[Profile]

    result = eval_typing(typing.PropsOnly[AllRelations])

    # Should have no properties
    fmt = format_helper.format_class(result)


def test_propsonly_empty_class():
    """PropsOnly should handle empty class."""
    result = eval_typing(typing.PropsOnly[EmptyClass])

    # Should return without error, likely NewProtocol or similar
    assert result is not None


def test_propsonly_with_generic_property():
    """PropsOnly should handle generic Property types."""

    class GenericModel:
        items: Property[list[str]]
        count: Property[int]

    result = eval_typing(typing.PropsOnly[GenericModel])

    fmt = format_helper.format_class(result)

    assert "items: list[str]" in fmt
    assert "count: int" in fmt
