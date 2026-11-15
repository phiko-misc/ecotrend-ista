"""Exception Class."""  # numpydoc ignore=ES01,EX01

from __future__ import annotations


class BaseError(Exception):  # numpydoc ignore=ES01,EX01
    """Base class for exceptions in this module.

    This is the base class for all custom exceptions in the module. It inherits
    from Python's built-in Exception class and can be used to catch errors specific
    to this module.
    """


class ServerError(BaseError):  # numpydoc ignore=ES01,EX01
    """Exception raised for server errors during requests.

    This exception is raised when a exception occurs during a request.
    It inherits from BaseError  and can be used to handle server-related
    issues specifically.
    """

    def __str__(self) -> str:
        """Return a string representation of the error.."""
        return "Server error occurred during the request"


class LoginError(BaseError):  # numpydoc ignore=ES01,EX01
    """Exception raised for login- and authentication related errors.

    This exception is raised when an authentication exception occurs during a request.
    It inherits from BaseError and is used specifically to handle issues related
    to authentication and login.
    """

    def __str__(self) -> str:
        """Return a string representation of an authentication error."""
        return "An authentication error occurred during the request"


class ParserError(ServerError):  # numpydoc ignore=ES01,EX01
    """Exception raised for errors encountered during parsing.

    This exception is raised when an error occurs during the parsing process
    of the request response. It inherits from BaseError and can be used
    to handle issues specifically related to parsing.
    """

    def __str__(self) -> str:
        """Return a string representation of parser error."""
        return "Error occurred during parsing of the request response"
