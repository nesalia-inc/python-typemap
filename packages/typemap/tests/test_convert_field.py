"""Tests for ConvertField type operator."""

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


# Define target types first to avoid forward references
class Profile:
    id: Property[int]
    bio: Property[str]


class Post:
    id: Property[int]
    title: Property[str]
    content: Property[str]
    author: Link[Profile]


# Test model with relations to already-defined types
class User:
    id: Property[int]
    name: Property[str]
    email: Property[str]
    posts: MultiLink[Post]  # one-to-many
    profile: Link[Profile]  # one-to-one


def test_convertfield_property():
    """ConvertField should return underlying type for Property fields."""
    result = eval_typing(typing.ConvertField[User, Literal["id"]])

    assert result is int


def test_convertfield_property_string():
    """ConvertField should return underlying type for string Property."""
    result = eval_typing(typing.ConvertField[User, Literal["name"]])

    assert result is str


def test_convertfield_with_nonexistent_key():
    """ConvertField should handle non-existent keys gracefully."""
    # This tests edge cases
    result = eval_typing(typing.ConvertField[User, Literal["nonexistent"]])

    # Should return something (the GetMemberType result)
    assert result is not None
