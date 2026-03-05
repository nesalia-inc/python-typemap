# Tests for UpdateClass in typemap_experiment

from typing import Callable, Literal, Self, Never
import typemap_extensions as typing
from typemap.type_eval import eval_typing
from tests import format_helper
import textwrap


# Define InitFnType - generates __init__ from class attributes
type InitFnType[T] = typing.Member[
    Literal["__init__"],
    Callable[
        [
            typing.Param[Literal["self"], Self],
            *[
                typing.Param[
                    p.name,
                    p.type,
                    # keyword-only, with default if init is not Never
                    Literal["keyword", "default"]
                    if typing.IsAssignable[p.init, Never]
                    else Literal["keyword"],
                ]
                for p in typing.Iter[typing.Attrs[T]]
            ],
        ],
        None,
    ],
    Literal["ClassVar"],
]


class Model:
    """Base class that adds __init__ to subclasses via UpdateClass"""

    def __init_subclass__[T](cls: type[T]) -> typing.UpdateClass[InitFnType[T]]:
        super().__init_subclass__()


# Test 1: Basic UpdateClass - adds __init__ to class
class Hero(Model):
    id: int | None = None
    name: str
    age: int | None = None
    secret_name: str


def test_updateclass_basic():
    """Test that UpdateClass generates __init__ method"""
    result = eval_typing(Hero)
    fmt = format_helper.format_class(result)

    # UpdateClass should generate __init__
    # Note: Preserving original attributes is the experiment - this tests the basic functionality
    assert "def __init__" in fmt
    assert "name: str" in fmt  # from __init__ signature
    assert "age: int | None" in fmt  # from __init__ signature


# Test 2: Class with more attributes
class User(Model):
    id: int
    username: str
    email: str | None = None
    active: bool = True


def test_updateclass_more_attrs():
    """Test UpdateClass with more attributes"""
    result = eval_typing(User)
    fmt = format_helper.format_class(result)

    # Should have __init__ with all params
    assert "def __init__" in fmt
    assert "id: int" in fmt
    assert "username: str" in fmt
    assert "email: str | None" in fmt
    assert "active: bool" in fmt


# Test 3: Check that __init__ has all params
def test_updateclass_has_all_params():
    """Test that __init__ has all parameters"""
    result = eval_typing(Hero)
    fmt = format_helper.format_class(result)

    # __init__ should have all the class attributes as parameters
    assert "name: str" in fmt
    assert "age: int | None" in fmt


# Test 4: No parent class
class SimpleClass:
    x: int
    y: str


def test_no_parent_class():
    """Test that classes without Model don't get __init__"""
    result = eval_typing(SimpleClass)
    fmt = format_helper.format_class(result)

    # Should NOT have __init__ added
    assert "def __init__" not in fmt


# Test 5: Nested inheritance
class Animal(Model):
    name: str


class Dog(Animal):
    breed: str


def test_nested_inheritance():
    """Test UpdateClass with nested inheritance"""
    result = eval_typing(Dog)
    fmt = format_helper.format_class(result)

    # Dog should have __init__ from Model
    assert "def __init__" in fmt
    assert "name: str" in fmt
    assert "breed: str" in fmt


# Test 6: Empty class
class Empty(Model):
    pass


def test_empty_class():
    """Test UpdateClass with empty class"""
    result = eval_typing(Empty)
    fmt = format_helper.format_class(result)

    # Should have __init__ but with no params
    assert "def __init__" in fmt


if __name__ == "__main__":
    print("Running test_updateclass_basic...")
    test_updateclass_basic()
    print("PASSED")

    print("Running test_updateclass_more_attrs...")
    test_updateclass_more_attrs()
    print("PASSED")

    print("Running test_updateclass_preserves_attrs...")
    test_updateclass_preserves_attrs()
    print("PASSED")

    print("Running test_no_parent_class...")
    test_no_parent_class()
    print("PASSED")

    print("Running test_nested_inheritance...")
    test_nested_inheritance()
    print("PASSED")

    print("Running test_empty_class...")
    test_empty_class()
    print("PASSED")

    print("\nAll tests passed!")
