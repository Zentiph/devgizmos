# pylint: disable=all

from abc import abstractmethod
from collections.abc import Buffer
from typing import (
    Iterable,
    Literal,
    Optional,
    Protocol,
    Self,
    SupportsBytes,
    SupportsIndex,
    SupportsComplex,
    SupportsFloat,
    SupportsInt,
    Tuple,
    TypeAlias,
    Union,
    overload,
)

ReadableBuffer: TypeAlias = Buffer

class _HasNumberDunder(Protocol):
    @abstractmethod
    def __number__(self) -> Union[Number, int, float, complex]:
        pass

ConvertibleToNumber: TypeAlias = _HasNumberDunder

class Number:
    @overload
    def __new__(
        cls,
        obj: Union[SupportsInt, SupportsFloat, SupportsComplex] = ...,
        /,
        *,
        preserve_type: bool = False,
    ) -> Number: ...
    @overload
    def __new__(
        cls, obj: Union[str, bytes, bytearray], base: SupportsIndex = 10, /
    ) -> Number: ...
    @overload
    def __new__(cls, obj: ConvertibleToNumber = ..., /) -> Number: ...
    def as_integer_ratio(self) -> Union[Tuple[int, int], None]: ...
    def hex(self) -> Union[str, None]: ...
    def is_integer(self) -> bool: ...
    @classmethod
    def fromhex(cls, string: str, /) -> Number: ...
    @property
    def real(self) -> Union[int, float]: ...
    @property
    def imag(self) -> Union[int, float]: ...
    @property
    def numerator(self) -> Union[int, None]: ...
    @property
    def denominator(self) -> Union[int, None]: ...
    @property
    def num_type(self) -> Literal["int", "float", "complex"]: ...
    def conjugate(self) -> Union[int, float, complex]: ...
    def bit_length(self) -> Union[int, None]: ...
    def bit_count(self) -> Union[int, None]: ...
    def to_bytes(
        self,
        length: SupportsIndex = 1,
        byteorder: Literal["little", "big"] = "big",
        *,
        signed: bool = False,
    ) -> Union[bytes, None]: ...
    @classmethod
    def from_bytes(
        cls,
        bytes: Iterable[SupportsIndex] | SupportsBytes | ReadableBuffer,
        byteorder: Literal["little", "big"] = "big",
        *,
        signed: bool = False,
    ) -> Number: ...
    def pow(
        self, exp: Union[int, float, complex, Number], mod: Optional[int] = None, /
    ) -> Number: ...
    def rpow(
        self, base: Union[int, float, complex, Number], mod: Optional[int] = None, /
    ) -> Number: ...
    def __add__(self, value: Union[int, float, complex, Number], /) -> Number: ...
    def __sub__(self, value: Union[int, float, complex, Number], /) -> Number: ...
    def __mul__(self, value: Union[int, float, complex, Number], /) -> Number: ...
    def __floordiv__(self, value: Union[int, float, complex, Number], /) -> Number: ...
    def __truediv__(self, value: Union[int, float, complex, Number], /) -> Number: ...
    def __mod__(self, value: Union[int, float, complex, Number], /) -> Number: ...
    def __divmod__(
        self, value: Union[int, float, complex, Number], /
    ) -> tuple[int, int]: ...
    def __radd__(self, value: int, /) -> Number: ...
    def __rsub__(self, value: int, /) -> Number: ...
    def __rmul__(self, value: int, /) -> Number: ...
    def __rfloordiv__(self, value: int, /) -> Number: ...
    def __rtruediv__(self, value: int, /) -> Number: ...
    def __rmod__(self, value: int, /) -> Number: ...
    def __rdivmod__(self, value: int, /) -> tuple[int, int]: ...
    def __pow__(
        self, value: Union[int, float, complex, Number], mod: Optional[int] = None, /
    ) -> complex: ...
    # Will not work if mod != None due to built-in pow() not attempting to call Number.__rpow__()
    def __rpow__(
        self, value: Union[int, float, complex, Number], mod: Optional[int] = None, /
    ) -> Number: ...
    def __and__(self, value: int, /) -> Number: ...
    def __or__(self, value: int, /) -> Number: ...
    def __xor__(self, value: int, /) -> Number: ...
    def __lshift__(self, value: int, /) -> Number: ...
    def __rshift__(self, value: int, /) -> Number: ...
    def __rand__(self, value: int, /) -> Number: ...
    def __ror__(self, value: int, /) -> Number: ...
    def __rxor__(self, value: int, /) -> Number: ...
    def __rlshift__(self, value: int, /) -> Number: ...
    def __rrshift__(self, value: int, /) -> Number: ...
    def __neg__(self) -> Number: ...
    def __pos__(self) -> Number: ...
    def __invert__(self) -> Number: ...
    def __trunc__(self) -> Number: ...
    def __ceil__(self) -> Number: ...
    def __floor__(self) -> Number: ...
    def __round__(self, ndigits: SupportsIndex = ..., /) -> Number: ...
    def __getnewargs__(self) -> tuple[int]: ...
    def __eq__(self, value: object, /) -> bool: ...
    def __ne__(self, value: object, /) -> bool: ...
    def __lt__(self, value: Union[int, float, complex, Number], /) -> bool: ...
    def __le__(self, value: Union[int, float, complex, Number], /) -> bool: ...
    def __gt__(self, value: Union[int, float, complex, Number], /) -> bool: ...
    def __ge__(self, value: Union[int, float, complex, Number], /) -> bool: ...
    def __float__(self) -> float: ...
    def __int__(self) -> int: ...
    def __abs__(self) -> Number: ...
    def __hash__(self) -> int: ...
    def __bool__(self) -> bool: ...
    def __index__(self) -> int: ...
    def __str__(self) -> str: ...
    def __repr__(self) -> str: ...
