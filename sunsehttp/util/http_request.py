"""Class definition for `Request`, a simple class used to abstract away from manually typing the http message format in."""

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from .exceptions import Limitation


class Request:
    """A python representation of the request body to send to a server/url. \n
    ### Request + `<type that conforms with Any, or tuple>`:
    This class overloads the + operator to allow for easier construction of requests. If `self.headers` is not supplied, you can add it to this request by supplying a tuple in the placeholder. If `self.data` is empty, you can supply any value.
    """

    def __init__(
        self,
        data: Any | None = None,
        headers: dict[str, int | str] | None = None,
        method: str = "GET",
        path: str = "/",
    ):
        """Constructs a `Request` with data and headers,

        Args:
            data (Any): The data for the request. Optional.
            headers (dict[str,Any] | None, optional): The headers supplied for the request. Defaults to None
        """
        self.data = data
        self.headers = headers if headers else {}
        self.method = method
        self.path = path

    def __add__(self, value: Any):
        if self.headers and self.data:
            raise Limitation(
                "Since the value of headers and data can be very ambiguous, we cannot make sure that the value is applied to the correct field without extra info, and since both fields are already filled, we can already assume that there is no work to be done."
            )
        if self.data:
            self.headers[value[0]] = value[1]
        if self.headers != {}:
            if isinstance(self.data, str) and isinstance(value, str):
                self.data += value
            if isinstance(self.data, bytes) and isinstance(value, bytes):
                self.data += value
            if isinstance(self.data, bytes) and isinstance(value, str):
                self.data += value.encode()
            else:
                raise Limitation(
                    "Can add with types that are str or bytes, not %s" % type(value)
                )

    def construct(self) -> bytes:
        """Constructs a byte string that conforms to a HTTP/1.1 request with the method."""
        res = ""
        res += f"{self.method.upper()} {self.path} HTTP/1.1\r\n"
        res += f"User-Agent: sunsehttp/0.1.0\r\n"
        res += f"Accept: */*\r\n"  # we can allow them to edit this later
        if self.headers:
            for i in self.headers:
                res += f"{i}: {self.headers[i]}\r\n"
        if self.method.upper() != "GET" or self.data:
            res += "\r\n"
            res += self.data  # pyright: ignore[reportOperatorIssue]
            # we can expect bytes and strs commonly here, but if we want more, we need to account for those
        return res.encode()


class Headers:
    """A class that represents the header value pairs that a server sends back as attributes, meaning you can access the value of a specific header by name, like `header.content_type` (Header names that contain hyphens are replaced to contain underscores instead, and all header names are lowercased.)"""

    def __init__(self):
        self.code = 0

    def instantiate(self, data: str):
        r = data.split("\r\n")
        self.code = int(r[0])
        r.pop(0)  # the response code
        # this class is only really used by the HEAD attr so we can expect to recieve responses with NO response body.
        for i in r:
            self.__setattr__(i.split(":")[0].lower().replace("-", "_"), i.split(":")[1])
        return self


class Options(Request):
    """A subclass of `Request`, but with extra metadata needed for constructing an OPTIONS request."""

    def __init__(self, target: str, path: str = "/"):
        """Constructs a `Request` with data and headers,

        Args:
            data (Any): The data for the request. Optional.
            headers (dict[str,Any] | None, optional): The headers supplied for the request. Defaults to None
        """
        super().__init__(method="OPTIONS", path=path)
        self.target = target

    def construct(self) -> bytes:
        """Constructs a byte string that conforms to a HTTP/1.1 request with the method."""
        res = ""
        res += f"{self.method.upper()} {self.target} HTTP/1.1\r\n"
        res += f"User-Agent: sunsehttp/0.1.0\r\n"
        res += f"Accept: */*\r\n"  # we can allow them to edit this later
        return res.encode()
