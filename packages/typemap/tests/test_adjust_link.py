"""Tests for AdjustLink type operator."""

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
    posts: MultiLink["Post"]  # one-to-many
    profile: Link["Profile"]  # one-to-one


class Post:
    id: Property[int]
    title: Property[str]
    author: Link[User]  # one-to-one


class Profile:
    id: Property[int]
    bio: Property[str]


def test_adjustlink_with_multilink():
    """AdjustLink should wrap in list when LinkTy is MultiLink."""
    result = eval_typing(typing.AdjustLink[Post, MultiLink[Post]])

    assert result.__origin__ is list
    assert result.__args__[0] is Post


def test_adjustlink_with_link():
    """AdjustLink should return type directly when LinkTy is Link (not MultiLink)."""
    result = eval_typing(typing.AdjustLink[Profile, Link[Profile]])

    assert result is Profile


def test_adjustlink_with_property():
    """AdjustLink should return type directly for Property (not a Link)."""
    result = eval_typing(typing.AdjustLink[int, Property[int]])

    # Property is not a Link, so should return as-is
    assert result is int


def test_adjustlink_with_sublcass_of_multilink():
    """AdjustLink should work with subclasses of MultiLink."""

    class MyMultiLink[T](MultiLink[T]):
        pass

    result = eval_typing(typing.AdjustLink[Post, MyMultiLink[Post]])

    assert result.__origin__ is list
    assert result.__args__[0] is Post


def test_adjustlink_with_singlelink():
    """AdjustLink should return type directly for SingleLink (subclass of Link but not MultiLink)."""

    class SingleLink[T](Link[T]):
        pass

    result = eval_typing(typing.AdjustLink[Profile, SingleLink[Profile]])

    # SingleLink is not MultiLink, so should return as-is
    assert result is Profile
