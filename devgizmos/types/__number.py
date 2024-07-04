"""
types.__number
==============
Contains the custom Number type.
"""

from math import ceil, floor, trunc
from re import match as re_match

from ..regex import COMPLEX_EXACT, COMPLEX_PARENS_EXACT, FLOAT_EXACT, INT_EXACT


class Number:
    """
    Number
    ======
    Represents a general number.
    """

    # pylint: disable=too-many-branches
    def __new__(cls, obj, base=10, /, *, preserve_type=False):
        """
        Number
        ======
        Represents a general number.
        Accepts any object with an __int__, __float__, or __complex__ method,
        or a convertible str, bytes, or bytearray.

        For custom object to Number implementations, define a __number__ method.
        If a __number__ method is found, that implementation will take priority.

        Parameters
        ----------
        :param obj: The object to convert to a Number.
        The object must have at least one number-conversion method (i.e. __int__, __float__, __complex__),
        or be a str, bytes, or bytearray.
        :type obj: ConvertibleToNumber | str | bytes | bytearray
        :param preserve_type: Whether to preserve the type of the number given, defaults to False.
        By default, Number will simplify given numbers as much as possible.
        ```python
        >>> num = Number((1+0j))
        >>> print(num)
        1
        ```
        :type preserve_type: bool, optional
        :param base: The base of the number.
        Only compatible when obj is a str, bytes, or bytearray and represents an int.
        :type base: SupportsIndex

        Raises
        ------
        :raises TypeError: If the object to convert is not a str, bytes, bytearray, or ConvertibleToNumber,

        Return
        ------
        :return: A new Char instance.
        :rtype: Self

        Example Usage
        -------------
        ```python
        >>> int_num = Number(3)
        >>> int_num + int_num
        6
        >>> float_num = Number(4.2)
        >>> float_num.is_integer()
        False
        >>> complex_num = Number((1+2j))
        >>> complex_num.conjugate()
        (1-2j)
        >>> base_16_num = Number("ff", 16)
        >>> print(base_16_num)
        255
        >>> class A:
        ...     def __init__(self, x):
        ...         self.x = x
        ...     def __number__(self): # custom number conversion implementation
        ...         return Number(self.x + 3)
        ...
        >>> a = A(3)
        >>> n = Number(a)
        >>> print(n)
        6
        ```
        """

        # ConvertibleToNumber implementation
        # (obj has __number__ method)
        if hasattr(obj, "__number__"):
            custom_val = obj.__number__()
            if not isinstance(custom_val, (int, float, complex, Number)):
                raise TypeError(
                    "__number__() implementation must return an "
                    + f"'int', 'float', 'complex', or 'Number' value, not '{type(custom_val).__name__}'"
                )

            instance = super().__new__(cls)
            instance._val = custom_val
            instance._num_type = type(custom_val)
            return instance

        if base != 0 and not 2 <= base <= 36:
            raise ValueError("Number() base must be >= 2 and <= 36, or 0")

        # if base is changed
        if base != 10 and isinstance(obj, (str, bytes, bytearray)):
            instance = super().__new__(cls)
            instance._val = int(obj, base)
            instance._num_type = int
            return instance

        # str implementation
        if isinstance(obj, str):
            int_match = re_match(INT_EXACT, obj)
            if int_match:
                instance = super().__new__(cls)
                instance._val = int(obj)
                instance._num_type = int
                return instance

            float_match = re_match(FLOAT_EXACT, obj)
            if float_match:
                instance = super().__new__(cls)
                instance._val = float(obj)
                instance._num_type = float
                return instance

            complex_match = re_match(COMPLEX_EXACT, obj)
            if complex_match:
                real, sign, imag = (
                    float(complex_match.group(1)),
                    complex_match.group(2),
                    float(complex_match.group(3)),
                )
                if sign == "-":
                    imag = -imag

                instance = super().__new__(cls)
                instance._val = complex(real, imag)
                instance._num_type = complex
                return instance

            complex_parens_match = re_match(COMPLEX_PARENS_EXACT, obj)
            if complex_parens_match:
                real, sign, imag = (
                    float(complex_parens_match.group(1)),
                    complex_parens_match.group(2),
                    float(complex_parens_match.group(3)),
                )
                if sign == "-":
                    imag = -imag

                instance = super().__new__(cls)
                instance._val = complex(real, imag)
                instance._num_type = complex
                return instance

            raise ValueError(f"invalid literal for Number(): '{obj}'")

        # SupportsNumType implementation
        # (obj has an __int__, __float__, or __complex__ method)
        if not (
            hasattr(obj, "__int__")
            or hasattr(obj, "__float__")
            or hasattr(obj, "__complex__")
        ):
            raise TypeError(
                "Number() argument must have either an '__int__', '__float__' or '__complex__' method"
            )

        # check __complex__ method first to preserve complexity
        # in case __float__ and __int__ methods exist and round
        # or destroy information
        if hasattr(obj, "__complex__"):
            c = complex(obj)
            if c.imag != 0 or preserve_type:
                val, num_type = c, complex
            else:
                f = c.real
                if not f.is_integer() or preserve_type:  # pylint: disable=no-member
                    val, num_type = f, float
                else:
                    val, num_type = int(f), int

        elif hasattr(obj, "__float__"):
            f = float(obj)
            if not f.is_integer() or preserve_type:
                val, num_type = f, float
            else:
                val, num_type = int(f), int

        # obj must have an __int__ method if it reaches this point due to above hasattr checks
        else:
            val, num_type = int(obj), int

        instance = super().__new__(cls)
        instance._val = val
        instance._num_type = num_type
        return instance

    def as_integer_ratio(self):
        """
        Return a pair of integers, whose ratio is equal to the original int.

        The ratio is in lowest terms and has a positive denominator.

        ```python
        >>> Number(10).as_integer_ratio()
        (10, 1)
        >>> Number(-10).as_integer_ratio()
        (-10, 1)
        >>> Number(0).as_integer_ratio()
        (0, 1)
        ```
        """

        if self._num_type in (int, float):
            return self._val.as_integer_ratio()

        # no method for complex
        raise TypeError("cannot express complex value as integer ratio")

    def hex(self):
        """Return a hexadecimal representation of a floating-point number.

        ```python
        >>> (-0.1).hex()
        '-0x1.999999999999ap-4'
        >>> 3.14159.hex()
        '0x1.921f9f01b866ep+1'
        ```
        """

        if self._num_type == float:
            return self._val.hex()

        raise TypeError("cannot express int or complex value as hex")

    def is_integer(self):
        """Return True if the Number is an integer."""

        if isinstance(self._val, complex):
            return self._val.real.is_integer()  # pylint: disable=no-member
        if isinstance(self._val, float):
            return self._val.is_integer()
        return True

    @classmethod
    def fromhex(cls, string, /):
        """
        Create a floating-point number from a hexadecimal string.

        ```python
        >>> float.fromhex('0x1.ffffp10')
        2047.984375
        >>> float.fromhex('-0x1p-1074')
        -5e-324
        ```
        """

        value = float.fromhex(string)
        return cls(value)

    @property
    def real(self):
        """the real part of a complex number"""

        if self._num_type in (int, float):
            return self._val

        return self._val.real

    @property
    def imag(self):
        """the imaginary part of a complex number"""

        if self._num_type in (int, float):
            return 0

        return self._val.imag

    @property
    def numerator(self):
        """the numerator of a rational number in lowest terms"""

        if self._num_type == int:
            return self._val

        if self._num_type == float:
            return self._val.as_integer_ratio()[0]

        raise TypeError("cannot express complex value as a numerator")

    @property
    def denominator(self):
        """the denominator of a rational number in lowest terms"""

        if self._num_type == int:
            return 1

        if self._num_type == float:
            return self._val.as_integer_ratio()[1]

        raise TypeError("cannot express complex value as a denominator")

    @property
    def num_type(self):
        """
        num_type
        ========
        Returns the type of number the Number represents.

        Return
        ------
        :return: The type of number the Number represents.
        :rtype: Literal["int", "float", "complex"]
        """

        return self._num_type.__name__

    def conjugate(self):
        """Returns self, the complex conjugate of any int."""

        if self._num_type == int:
            return self._val

        if self._num_type == float:
            return self._val

        return self._val.conjugate()

    def bit_length(self):
        """
        Number of bits necessary to represent self in binary.

        ```python
        >>> bin(37)
        '0b100101'
        >>> (37).bit_length()
        6
        ```
        """

        if self._num_type == int:
            return self._val.bit_length()

        raise TypeError("cannot express float or complex value as bit length")

    def bit_count(self):
        """
        Number of ones in the binary representation of the absolute value of self.

        Also known as the population count.

        ```python
        >>> bin(13)
        '0b1101'
        >>> (13).bit_count()
        3
        ```
        """

        if self._num_type == int:
            return self._val.bit_count()

        raise TypeError("cannot express float or complex value as population count")

    def to_bytes(self, length=1, byteorder="big", *, signed=False):
        """
        Return an array of bytes representing an integer.

        length
            Length of bytes object to use.
            An OverflowError is raised if the integer is not representable
            with the given number of bytes.
            Default is length 1.
        byteorder
            The byte order used to represent the integer.
            If byteorder is 'big', the most significant byte is at the beginning of the byte array.
            If byteorder is 'little', the most significant byte is at the end of the byte array.
            To request the native byte order of the host system, use sys.byteorder as the byte order value.
            Default is to use 'big'.
        signed
            Determines whether two's complement is used to represent the integer.
            If signed is False and a negative integer is given, an OverflowError is raised.
        """

        if self._num_type == int:
            return self._val.to_bytes(length, byteorder, signed=signed)

        raise TypeError("cannot convert float or complex value to bytes")

    # pylint: disable=redefined-builtin
    @classmethod
    def from_bytes(cls, bytes, byteorder="big", *, signed=False):
        """
        Return the integer represented by the given array of bytes.

        bytes
            Holds the array of bytes to convert.
            The argument must either support the buffer protocol
            or be an iterable object producing bytes.
            Bytes and bytearray are examples of built-in objects that support the buffer protocol.
        byteorder
            The byte order used to represent the integer.
            If byteorder is 'big', the most significant byte is at the beginning of the byte array.
            If byteorder is 'little', the most significant byte is at the end of the byte array.
            To request the native byte order of the host system, use sys.byteorder as the byte order value.
            Default is to use 'big'.
        signed
            Indicates whether two's complement is used to represent the integer.
        """

        value = int.from_bytes(bytes, byteorder, signed=signed)
        return cls(value)

    def pow(self, exp, mod=None, /):
        """
        pow
        ===
        Returns Number**exp % mod.
        Custom pow function to circumvent built-in
        pow() not recognizing Number.__rpow__() method.

        Parameters
        ----------
        :param exp: The value to raise the Number to.
        :type exp: int | float | complex | Number
        :param mod: The modulus to perform on the exponential value, defaults to None.
        Only compatible with integer exp values.
        :type mod: int | None, optional

        Return
        ------
        :return: The Number raised to the power, with modulus applied if mod is not None.
        :rtype: Number
        """

        return Number(pow(self._val, exp, mod))

    def rpow(self, base, mod=None, /):
        """
        rpow
        ====
        Returns base**Number % mod.
        Custom reverse power function to circumvent built-in
        pow() not recognizing Number.__rpow__() method.

        Parameters
        ----------
        :param base: The base that will be raises to the power of Number.
        :type base: int | float | complex | Number
        :param mod: The modulus to perform on the exponential value, defaults to None.
        Only compatible with integer exp values.
        :type mod: int | None, optional

        Return
        ------
        :return: The Number raised to the power, with modulus applied if mod is not None.
        :rtype: Number
        """

        return Number(pow(base, self._val, mod))

    def __add__(self, value, /):
        if not isinstance(value, (int, float, complex, Number)):
            raise TypeError(
                f"unsupported operand type(s) for + ('Number' and '{type(value).__name__}')"
            )

        return Number(self._val + value)

    def __sub__(self, value, /):
        if not isinstance(value, (int, float, complex, Number)):
            raise TypeError(
                f"unsupported operand type(s) for - ('Number' and '{type(value).__name__}')"
            )

        return Number(self._val - value)

    def __mul__(self, value, /):
        if not isinstance(value, (int, float, complex, Number)):
            raise TypeError(
                f"unsupported operand type(s) for * ('Number' and '{type(value).__name__}')"
            )

        return Number(self._val * value)

    def __floordiv__(self, value, /):
        if not isinstance(value, (int, float, complex, Number)):
            raise TypeError(
                f"unsupported operand type(s) for // ('Number' and '{type(value).__name__}')"
            )

        return Number(self._val // value)

    def __truediv__(self, value, /):
        if not isinstance(value, (int, float, complex, Number)):
            raise TypeError(
                f"unsupported operand type(s) for / ('Number' and '{type(value).__name__}')"
            )

        return Number(self._val / value)

    def __mod__(self, value, /):
        if not isinstance(value, (int, float, complex, Number)):
            raise TypeError(
                f"unsupported operand type(s) for % ('Number' and '{type(value).__name__}')"
            )

        return Number(self._val % value)

    def __divmod__(self, value, /):
        if not isinstance(value, (int, float, complex, Number)):
            raise TypeError(
                f"unsupported operand type(s) for divmod(): 'Number' and '{type(value).__name__}'"
            )

        return divmod(self._val, value)

    def __radd__(self, value, /):
        if not isinstance(value, (int, float, complex, Number)):
            raise TypeError(
                f"unsupported operand type(s) for + ('{type(value).__name__}' and 'Number')"
            )

        return Number(value + self._val)

    def __rsub__(self, value, /):
        if not isinstance(value, (int, float, complex, Number)):
            raise TypeError(
                f"unsupported operand type(s) for - ('{type(value).__name__}' and 'Number')"
            )

        return Number(value - self._val)

    def __rmul__(self, value, /):
        if not isinstance(value, (int, float, complex, Number)):
            raise TypeError(
                f"unsupported operand type(s) for * ('{type(value).__name__}' and 'Number')"
            )

        return Number(value * self._val)

    def __rfloordiv__(self, value, /):
        if not isinstance(value, (int, float, complex, Number)):
            raise TypeError(
                f"unsupported operand type(s) for // ('{type(value).__name__}' and 'Number')"
            )

        return Number(value // self._val)

    def __rtruediv__(self, value, /):
        if not isinstance(value, (int, float, complex, Number)):
            raise TypeError(
                f"unsupported operand type(s) for / ('{type(value).__name__}' and 'Number')"
            )

        return Number(value / self._val)

    def __rmod__(self, value, /):
        if not isinstance(value, (int, float, complex, Number)):
            raise TypeError(
                f"unsupported operand type(s) for % ('{type(value).__name__}' and 'Number')"
            )

        return Number(value % self._val)

    def __rdivmod__(self, value, /):
        if not isinstance(value, (int, float, complex, Number)):
            raise TypeError(
                f"unsupported operand type(s) for divmod(): '{type(value).__name__}' and 'Number'"
            )

        return divmod(value, self._val)

    def __pow__(self, value, mod=None, /):
        if not isinstance(value, (int, Number)):
            raise TypeError(
                "unsupported operand type(s) for ** or pow():"
                + f"'Number', '{type(value).__name__}', '{type(mod).__name__}'"
            )

        if isinstance(value, Number):
            return Number(pow(self._val, value._val, mod))
        return Number(pow(self._val, value, mod))

    # Will not work if mod != None due to built-in pow() not attempting to call Number.__rpow__()
    def __rpow__(self, value, mod=None, /):
        if not isinstance(value, (int, Number)):
            raise TypeError(
                "unsupported operand type(s) for ** or pow():"
                + f"'{type(value).__name__}', 'Number', '{type(mod).__name__}'"
            )

        if isinstance(value, Number):
            return Number(pow(value._val, self._val, mod))
        return Number(pow(value, self._val, mod))

    def __and__(self, value, /):
        if not isinstance(value, (int, Number)):
            raise TypeError(
                f"unsupported operand type(s) for &: 'Number' and '{type(value).__name__}'"
            )

        if isinstance(value, Number):
            return Number(self._val & value._val)
        return Number(self._val & value)

    def __or__(self, value, /):
        if not isinstance(value, (int, Number)):
            raise TypeError(
                f"unsupported operand type(s) for |: 'Number' and '{type(value).__name__}'"
            )

        if isinstance(value, Number):
            return Number(self._val | value._val)
        return Number(self._val | value)

    def __xor__(self, value, /):
        if not isinstance(value, (int, Number)):
            raise TypeError(
                f"unsupported operand type(s) for ^: 'Number' and '{type(value).__name__}'"
            )

        if isinstance(value, Number):
            return Number(self._val ^ value._val)
        return Number(self._val ^ value)

    def __lshift__(self, value, /):
        if not isinstance(value, (int, Number)):
            raise TypeError(
                f"unsupported operand type(s) for <<: 'Number' and '{type(value).__name__}'"
            )

        if isinstance(value, Number):
            return Number(self._val << value._val)
        return Number(self._val << value)

    def __rshift__(self, value, /):
        if not isinstance(value, (int, Number)):
            raise TypeError(
                f"unsupported operand type(s) for >>: 'Number' and '{type(value).__name__}'"
            )

        if isinstance(value, Number):
            return Number(self._val >> value._val)
        return Number(self._val >> value)

    def __rand__(self, value, /):
        if not isinstance(value, (int, Number)):
            raise TypeError(
                f"unsupported operand type(s) for &: '{type(value).__name__}' and 'Number'"
            )

        if isinstance(value, Number):
            return Number(value._val & self._val)
        return Number(value & self._val)

    def __ror__(self, value, /):
        if not isinstance(value, (int, Number)):
            raise TypeError(
                f"unsupported operand type(s) for |: '{type(value).__name__}' and 'Number'"
            )

        if isinstance(value, Number):
            return Number(value._val | self._val)
        return Number(value | self._val)

    def __rxor__(self, value, /):
        if not isinstance(value, (int, Number)):
            raise TypeError(
                f"unsupported operand type(s) for ^: '{type(value).__name__}' and 'Number'"
            )

        if isinstance(value, Number):
            return Number(value._val ^ self._val)
        return Number(value ^ self._val)

    def __rlshift__(self, value, /):
        if not isinstance(value, (int, Number)):
            raise TypeError(
                f"unsupported operand type(s) for <<: '{type(value).__name__}' and 'Number'"
            )

        if isinstance(value, Number):
            return Number(value._val << self._val)
        return Number(value << self._val)

    def __rrshift__(self, value, /):
        if not isinstance(value, (int, Number)):
            raise TypeError(
                f"unsupported operand type(s) for >>: '{type(value).__name__}' and 'Number'"
            )

        if isinstance(value, Number):
            return Number(value._val >> self._val)
        return Number(value >> self._val)

    def __neg__(self):
        # pylint: disable=invalid-unary-operand-type
        return Number(-self._val)

    def __pos__(self):
        # pylint: disable=invalid-unary-operand-type
        return Number(+self._val)

    def __invert__(self):
        if self._num_type != int:
            raise TypeError(
                f"bad operand type for unary ~: '{type(self._val).__name__}'. only use if the Number is an int."
            )

        # pylint: disable=invalid-unary-operand-type
        return Number(~self._val)

    def __trunc__(self):
        return Number(trunc(self._val))

    def __ceil__(self):
        return Number(ceil(self._val))

    def __floor__(self):
        return Number(floor(self._val))

    def __round__(self, ndigits, /):
        return Number(round(self._val, ndigits))

    def __getnewargs__(self):
        return (self._val,)

    def __eq__(self, value, /):
        if isinstance(value, (int, float, complex)):
            return self._val == value
        if isinstance(value, Number):
            return self._val == value._val
        return False

    def __lt__(self, value, /):
        if not isinstance(value, (int, float, complex, Number)):
            raise TypeError(
                f"unsupported operand type(s) for <: 'Number' and '{type(value).__name__}'"
            )

        if isinstance(value, Number):
            return self._val < value._val
        return self._val < value

    def __le__(self, value, /):
        if not isinstance(value, (int, float, complex, Number)):
            raise TypeError(
                f"unsupported operand type(s) for <=: 'Number' and '{type(value).__name__}'"
            )

        if isinstance(value, Number):
            return self._val <= value._val
        return self._val <= value

    def __gt__(self, value, /):
        if not isinstance(value, (int, float, complex, Number)):
            raise TypeError(
                f"unsupported operand type(s) for >: 'Number' and '{type(value).__name__}'"
            )

        if isinstance(value, Number):
            return self._val > value._val
        return self._val > value

    def __ge__(self, value, /):
        if not isinstance(value, (int, float, complex, Number)):
            raise TypeError(
                f"unsupported operand type(s) for >=: 'Number' and '{type(value).__name__}'"
            )

        if isinstance(value, Number):
            return self._val >= value._val
        return self._val >= value

    def __float__(self):
        return float(self._val)

    def __int__(self):
        return int(self._val)

    def __abs__(self):
        return Number(abs(self._val))

    def __hash__(self):
        return hash(self._val)

    def __bool__(self):
        return bool(self._val)

    def __index__(self):
        if self._num_type in ("float", "complex"):
            raise TypeError("cannot create an index value from a non-integer Number")

        return self._val

    def __str__(self):
        return str(self._val)

    def __repr__(self):
        return f"{self.__class__.__name__}({self._val})"
