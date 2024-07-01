"""
types.__char
============
Contains the custom Char type.
"""


class Char:
    """
    Char
    ====
    Represents a single character string.
    """

    def __new__(cls, obj, /):
        """
        Char
        ====
        Represents a single character string.

        Parameters
        ----------
        :param obj: The object to convert to a Char. The object must have a __str__ method.
        :type obj: Any

        Raises
        ------
        :raises TypeError: If the object to convert does not have a __str__ method.
        :raises ValueError: If len(str(object)) != 1.

        Return
        ------
        :return: A new Char instance.
        :rtype: Self

        Example Usage
        -------------
        ```python
        >>> my_char = Char("x")
        >>> my_char.upper()
        X
        >>> my_char.isalpha()
        True
        >>> my_new_char = Char("AB")
        TypeError: Char() argument must have a length of 1, not 2
        ```
        """

        if not hasattr(obj, "__str__"):
            raise TypeError("Char() argument must have a '__str__' method")

        val = str(obj)

        if len(val) != 1:
            raise ValueError(f"Char() argument must have a length of 1, not {len(val)}")

        instance = super().__new__(cls)
        instance._val = val
        return instance

    def capitalize(self):
        """
        Return a capitalized version of the Char.

        Works identically to Char.upper(), but exists to
        maintain similarity with str.
        """

        return Char(self._val.upper())

    def casefold(self):
        """Return a value of the Char suitable for caseless comparisons."""

        return self._val.lower()

    def encode(self, encoding="utf-8", errors="strict"):
        """
        Encode the Char using the codec registered for encoding.

        encoding
            The encoding in which to encode the Char.
        errors
            The error handling scheme to use for encoding errors.
        The default is 'strict' meaning that encoding errors raise a UnicodeEncodeError.
        Other possible values are 'ignore', 'replace' and 'xmlcharrefreplace'
        as well as any other name registered with codecs.register_error
        that can handle UnicodeEncodeErrors.
        """

        return str(self._val).encode(encoding, errors)

    def isalnum(self):
        """Return True if the Char is alpha-numeric, False otherwise."""

        return self._val.isalnum()

    def isalpha(self):
        """Return True if the Char is alphabetic, False otherwise."""

        return self._val.isalpha()

    def isascii(self):
        """
        Return True if the Char is ASCII, False otherwise.

        ASCII characters have code points in the range U+0000-U+007F
        """

        return self._val.isascii()

    def isdecimal(self):
        """Return True if the Char is a decimal, False otherwise."""

        return self._val.isdecimal()

    def isdigit(self):
        """Return True if the Char is a digit, False otherwise."""

        return self._val.isdigit()

    def islower(self):
        """Return True if the Char is lowercase, False otherwise."""

        return self._val.islower()

    def isnumeric(self):
        """Return True if the Char is numeric, False otherwise."""

        return self._val.isnumeric()

    def isprintable(self):
        """Return True if the Char is printable, False otherwise."""

        return self._val.isprintable()

    def isspace(self):
        """Return True if the Char is whitespace, False otherwise."""

        return self._val.isspace()

    def isupper(self):
        """Return True if the Char is uppercase, False otherwise."""

        return self._val.isupper()

    def join(self, iterable, /):
        """Concatenate any number of strings.

        The Char whose method is called is inserted in between each given string.
        The result is returned as a new string.

        Example: Char('.').join(['ab', 'pq', 'rs']) -> 'ab.pq.rs'
        """

        return self._val.join(iterable)

    def lower(self):
        """Return a copy of the Char converted to lowercase."""

        return self._val.lower()

    def swapcase(self):
        """
        If the Char is uppercase, swap it to lowercase.
        If it is lowercase, swap it to uppercase.
        """

        return self._val.swapcase()

    def upper(self):
        """Return a copy of the Char converted to uppercase."""

        return self._val.upper()

    def __add__(self, value, /):
        if not isinstance(value, (str, Char)):
            raise TypeError(
                f"unsupported operand type(s) for + ('Char' and '{type(value).__name__}')"
            )

        return self._val + str(value)

    def __contains__(self, key, /):
        if not isinstance(key, (str, Char)):
            raise TypeError(
                f"'in <Char>' requires string or Char as left operand, not {type(key).__name__}"
            )

        return key in self._val

    def __eq__(self, value, /):
        if isinstance(value, Char):
            return self._val == value._val

        if isinstance(value, str):
            if len(value) == 1:
                return self._val == value

        return False

    def __ge__(self, value, /):
        if not isinstance(value, (Char, str)):
            raise TypeError(
                f"'>=' not supported between instances of 'Char' and '{type(value).__name__}'"
            )

        if isinstance(value, Char):
            return self._val >= value._val

        return self._val >= value

    def __getitem__(self, key, /):
        return self._val[key]

    def __gt__(self, value, /):
        if not isinstance(value, (Char, str)):
            raise TypeError(
                f"'>' not supported between instances of 'Char' and '{type(value).__name__}'"
            )

        if isinstance(value, Char):
            return self._val > value._val

        return self._val > value

    def __hash__(self):
        return hash(self._val)

    def __iter__(self):
        return iter(self._val)

    def __le__(self, value, /):
        if not isinstance(value, (Char, str)):
            raise TypeError(
                f"'<=' not supported between instances of 'Char' and '{type(value).__name__}'"
            )

        if isinstance(value, Char):
            return self._val <= value._val

        return self._val <= value

    def __len__(self):
        return 1

    def __lt__(self, value, /):
        if not isinstance(value, (Char, str)):
            raise TypeError(
                f"'<' not supported between instances of 'Char' and '{type(value).__name__}'"
            )

        if isinstance(value, Char):
            return self._val < value._val

        return self._val < value

    def __mul__(self, value, /):
        return self._val * value

    def __bool__(self):
        return True

    def __bytes__(self):
        return bytes(self._val, "utf-8")

    def __complex__(self):
        return complex(self._val)

    def __float__(self):
        return float(self._val)

    def __int__(self):
        return int(self._val)

    def __str__(self):
        return self._val

    def __repr__(self):
        return f"{self.__class__.__name__}({self._val!r})"

    def __getnewargs__(self):
        return (self._val,)
