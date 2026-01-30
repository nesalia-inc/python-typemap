# TODO: Integrate this as a runtime test

# Simulate array broadcasting

from typing import Literal as L

from typing import (
    Literal,
    Never,
    GetArg,
    Bool,
    Matches,
    Iter,
    Slice,
    Length,
    IsSub,
    RaiseError,
)


class Array[DType, *Shape]:
    def __add__[*Shape2](
        self,
        other: Array[DType, *Shape2]
    ) -> Array[DType, *Merge[tuple[*Shape], tuple[*Shape2]]]:
        raise BaseException


type AppendTuple[A, B] = tuple[
    *[x for x in Iter[A]],
    B,
]

type MergeOne[T, S] = (
    T
    if Matches[T, S] or Matches[S, Literal[1]]
    else S if Matches[T, Literal[1]]
    else RaiseError[Literal["Broadcast mismatch"], T, S]
)

type DropLast[T] = Slice[T, Literal[0], Literal[-1]]
type Last[T] = GetArg[T, tuple, Literal[-1]]

# Matching on Never here is intentional; it prevents stupid
# infinite recursions.
type Empty[T] = IsSub[Length[T], Literal[0]]

type Merge[T, S] = (
    S if Bool[Empty[T]] else T if Bool[Empty[S]]
    else
    AppendTuple[
        Merge[DropLast[T], DropLast[S]],
        MergeOne[Last[T], Last[S]]
    ]
)

a1: Array[float, L[4], L[1]]
a2: Array[float, L[3]]
ar = a1 + a2
reveal_type(ar)  # N: Revealed type is "__main__.Array[builtins.float, Literal[4], Literal[3]]"
checkr: Array[float, L[4], L[3]] = ar


b1: Array[float, int, int]
b2: Array[float, int]
reveal_type(b1 + b2)  # N: Revealed type is "__main__.Array[builtins.float, builtins.int, builtins.int]"


c1: Array[float, L[4], L[1], L[5]]
c2: Array[float, L[4], L[3], L[1]]
reveal_type(c1 + c2)  # N: Revealed type is "__main__.Array[builtins.float, Literal[4], Literal[3], Literal[5]]"

#

err1: Array[float, L[4], L[2]]
err2: Array[float, L[3]]
err1 + err2  # E: Broadcast mismatch: Literal[2], Literal[3]
