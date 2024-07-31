"""
types.__char
============
Contains the custom Char type.
"""

from ..errguards import ensure_instance_of


class Char:
    """Represents a single character string."""

    def __new__(cls, obj, /, *, truncate=False):
        """
        Char()
        ------
        Represents a single character string.
        Accepts any object with a __str__ method.

        For custom object to Char implementations, define a __char__ method.
        If a __char__ method is found, that implementation will take priority.

        Parameters
        ~~~~~~~~~~
        :param obj: The object to convert to a Char. The object must have a __str__ method.
        :type obj: ConvertibleToStr | ConvertibleToChar
        :param truncate: Whether to truncate the given object if necessary, defaults to False.
        :type truncate: bool, optional

        Raises
        ~~~~~~
        :raises TypeError: If the object to convert does not have a __str__ or __char__ method.
        :raises ValueError: If len(str(object)) != 1 and not truncate.

        Return
        ~~~~~~
        :return: A new Char instance.
        :rtype: Self

        Example Usage
        ~~~~~~~~~~~~~
        >>> my_char = Char("x")
        >>> my_char.upper()
        X
        >>> my_char.isalpha()
        True
        >>> my_new_char = Char("AB")
        TypeError: Char() argument must have a length of 1, not 2
        """

        # type checks (part 1)
        ensure_instance_of(truncate, bool)

        # ConvertibleToChar implementation
        # (obj has __char__ method)
        if hasattr(obj, "__char__"):
            custom_val = obj.__char__()

            # type checks
            ensure_instance_of(
                custom_val,
                str,
                Char,
                msg=f"__char__() implementation must return a 'str' or 'Char' value, not '{type(custom_val).__name__}",
            )

            # value checks
            if len(custom_val) != 1:
                if truncate:
                    custom_val = custom_val[0]
                else:
                    raise ValueError(
                        f"Char() argument must have a length of 1, not {len(custom_val)}"
                    )

            instance = super().__new__(cls)
            instance._val = custom_val
            return instance

        # str implementation
        # type checks
        if not hasattr(obj, "__str__"):
            raise TypeError("Char() argument must have a '__str__' method")

        val = str(obj)

        # value checks
        if len(val) != 1:
            if truncate:
                val = val[0]
            else:
                raise ValueError(
                    f"Char() argument must have a length of 1, not {len(val)}"
                )

        instance = super().__new__(cls)
        instance._val = val
        return instance

    def capitalize(self):
        """
        Char().capitalize()
        -------------------
        Return a capitalized version of the Char.

        Works identically to Char.upper(), but exists to
        maintain similarity with str.

        Return
        ~~~~~~
        :return: The capitalized Char.
        :rtype: Char
        """

        return Char(self._val.upper())

    def casefold(self):
        """
        Char().casefold()
        -----------------
        Return a value of the Char suitable for caseless comparisons.

        Return
        ~~~~~~
        :return: The casefold Char.
        :rtype: Char
        """

        return Char(self._val.lower())

    # the long lines are regretful to implement
    # but necessary for the new pylance docstring parsing
    # to properly read the docstring
    # pylint: disable=line-too-long
    def encode(self, encoding="utf-8", errors="strict"):
        """
        Char().encode()
        ---------------
        Encode the Char using the codec registered for encoding.

        Parameters
        ~~~~~~~~~~
        :param encoding: The encoding in which to encode the Char.
        :type encoding: str
        :param errors: The error handling scheme to use for encoding errors. The default is 'strict' meaning that encoding errors raise a UnicodeEncodeError.
        Other possible values are 'ignore', 'replace' and 'xmlcharrefreplace' as well as any other name registered with codecs.register_error that can handle UnicodeEncodeErrors.
        :type errors: str
        """

        return self._val.encode(encoding, errors)

    def isalnum(self):
        """
        Char().isalnum()
        ----------------
        Return True if the Char is alpha-numeric, False otherwise.

        Return
        ~~~~~~
        :return: True if the Char is alpha-numeric, False otherwise.
        :rtype: bool
        """

        return self._val.isalnum()

    def isalpha(self):
        """
        Char().isalpha()
        ----------------
        Return True if the Char is alphabetic, False otherwise.

        Return
        ~~~~~~
        :return: True if the Char is alphabetic, False otherwise.
        :rtype: bool
        """

        return self._val.isalpha()

    def isascii(self):
        """
        Char().isascii()
        ----------------
        Return True if the Char is ASCII, False otherwise.

        ASCII characters have code points in the range U+0000-U+007F.

        Return
        ~~~~~~
        :return: True if the Char is ASCII, False otherwise.
        :rtype: bool
        """

        return self._val.isascii()

    def isdecimal(self):
        """
        Char().isdecimal()
        ------------------
        Return True if the Char is a decimal, False otherwise.

        Return
        ~~~~~~
        :return: True if the Char is a decimal, False otherwise.
        :rtype: bool
        """

        return self._val.isdecimal()

    def isdigit(self):
        """
        Char().isdigit()
        ----------------
        Return True if the Char is a digit, False otherwise.

        Return
        ~~~~~~
        :return: True if the Char is a digit, False otherwise.
        :rtype: bool
        """

        return self._val.isdigit()

    def islower(self):
        """
        Char().islower()
        ----------------
        Return True if the Char is lowercase, False otherwise.

        Return
        ~~~~~~
        :return: True if the Char is lowercase, False otherwise.
        :rtype: bool
        """

        return self._val.islower()

    def isnumeric(self):
        """
        Char().isnumeric()
        ------------------
        Return True if the Char is numeric, False otherwise.

        Return
        ~~~~~~
        :return: True if the Char is numeric, False otherwise.
        :rtype: bool
        """

        return self._val.isnumeric()

    def isprintable(self):
        """
        Char().isprintable()
        --------------------
        Return True if the Char is printable, False otherwise.

        Return
        ~~~~~~
        :return: True if the Char is printable, False otherwise.
        :rtype: bool
        """

        return self._val.isprintable()

    def isspace(self):
        """
        Char().isspace()
        ----------------
        Return True if the Char is whitespace, False otherwise.

        Return
        ~~~~~~
        :return: True if the Char is whitespace, False otherwise.
        :rtype: bool
        """

        return self._val.isspace()

    def isupper(self):
        """
        Char().isupper()
        ----------------
        Return True if the Char is uppercase, False otherwise.

        Return
        ~~~~~~
        :return: True if the Char is uppercase, False otherwise.
        :rtype: bool
        """

        return self._val.isupper()

    def join(self, iterable, /):
        """
        Char().join()
        -------------
        Concatenate any number of strings.

        The Char whose method is called is inserted in between each given string.
        The result is returned as a new string.

        Example: Char('.').join(['ab', 'pq', 'rs']) -> 'ab.pq.rs'

        Return
        ~~~~~~
        :return: The concatenated strings using the Char.
        :rtype: str
        """

        return self._val.join(iterable)

    def lower(self):
        """
        Char().lower()
        --------------
        Return a copy of the Char converted to lowercase.

        Return
        ~~~~~~
        :return: A copy of the Char converted to lowercase.
        :rtype: Char
        """

        return Char(self._val.lower())

    def swapcase(self):
        """
        Char().swapcase()
        -----------------
        If the Char is uppercase, convert it to lowercase.
        If it is lowercase, convert it to uppercase.

        Return
        ~~~~~~
        :return: The swapped Char.
        :rtype: Char
        """

        return Char(self._val.swapcase())

    def upper(self):
        """
        Char().upper()
        --------------
        Return a copy of the Char converted to uppercase.

        Return
        ~~~~~~
        :return: A copy of the Char converted to uppercase.
        :rtype: Char
        """

        return Char(self._val.upper())

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
        return f"Char({self._val!r})"

    def __getnewargs__(self):
        return (self._val,)
