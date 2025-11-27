"""Contains the definition of the response the client gets after sending a request."""

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from .exceptions import ContinuationWarning, ClientError
    from .constants import error_code_reasons


class Response:
    def __init__(self):
        """Internal, don't use this constructor for creating a response, if on server side. Use the equivalent `ServerResponse` defined in the `sunsehttp.server` module. (not available as of v0.1.0)"""
        self.headers: list[dict] = []
        """A list of all the headers, seperated into key value pairs."""
        self.data: Any | None = None
        """The data/response body."""
        self.code: int = 0
        """The response code."""
        self.phrase: str = ""
        """The phrase associated with the response code, according to RFC 2616, Section 6.1.1."""
        self.error_info = None

    @classmethod
    def parse(cls, incoming: bytes, strict_error: bool):
        inited = cls()
        response = incoming.decode()
        code_header_data = response.split("\r\n")
        inited.code = int(code_header_data[0].split()[1])
        inited.phrase = code_header_data[0].split("")[2]
        if strict_error:
            if inited.code >= 300 < 400:
                raise ContinuationWarning(
                    "This request requires you to continue. Take necessary action. This was generated due to the strict error param being enabled. To silence these warnings/errors, set the strict_error param on your request to False, or just don't set it at all."
                )
            if inited.code >= 400:
                cls.error_info = ClientError()
                cls.error_info.reason = error_code_reasons[inited.code]
                raise ClientError(
                    "Code of above (or equal to) 400 was detected, indicating a client, AND/OR server side error. Check this error's `reason` attribute through the `error_info` attribute to see why. To silence these warnings/errors, set the strict_error param on your request to False, or just don't set it at all."
                )
