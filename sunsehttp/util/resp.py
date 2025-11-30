"""Contains the definition of the response the client gets after sending a request."""

from typing import Any, Literal, TYPE_CHECKING, Callable, BinaryIO
import gzip


from .exceptions import ClientError
from .constants import error_code_reasons

if TYPE_CHECKING:
    from .._http import Client


class Response:
    def __init__(self):
        """Internal, don't use this constructor for creating a response, if on server side. Use the equivalent `ServerResponse` defined in the `sunsehttp.server` module. (not available as of v0.1.0)"""
        self.headers: list[dict[str, int | str]] = []
        """A list of all the headers, seperated into key value pairs."""
        self.data: bytes | None = None
        """The data/response body, if applicable."""
        self.code: int = 0
        """The response code."""
        self.phrase: str = ""
        """The phrase associated with the response code, according to RFC 2616, Section 6.1.1."""
        self.error_info = None
        self.encoding: str = ""
        """The encoding of the response body."""
        self.unencoder_func = ""
        """The custom function that was provided to unencode the contents."""

    @classmethod
    def _parse(
        cls,
        incoming: bytes,
        strict_error: bool,
        unencoder: Callable[..., bytes] | None = None,
    ):
        """parses headers, and leaves data as bytes so the decoding algorithm can do its work"""
        inited = cls()
        response = incoming
        code_header_data = response.split(b"\n")  # so we keep the \r as a marker
        inited.code = int(code_header_data[0].split()[1])
        inited.phrase = code_header_data[0].split()[2].decode()
        code_header_data.pop(0)
        for n, i in enumerate(code_header_data):
            if b":" in i:
                header_val = i.decode().split(":")
                inited.headers.append({header_val[0]: header_val[1].removesuffix("\r")})
                # this basically says "if I contain a colon (meaning it's a header), decode me and put me into self.headers"
            if i == b"\r":
                inited.data = incoming[n + 1 :]
                # n + 1 so we don't include the empty \r line
        if strict_error:
            if inited.code >= 400:
                inited.error_info = ClientError()
                inited.error_info.reason = error_code_reasons[inited.code]
                raise ClientError(
                    "Code of above (or equal to) 400 was detected, indicating a client, AND/OR server side error. Check this error's `reason` attribute through the `error_info` attribute to see why. To silence these warnings/errors, set the strict param on your request to False, or just don't set it at all."
                )
        if inited.data:
            for i, v in inited.headers:
                if i == "Content-Encoding":
                    inited.encoding = v
                    match v:
                        case "gzip":
                            inited.unencode_gzip()
                        case "identity":
                            return inited
                        case _:
                            if unencoder:
                                unencoder(inited.data)
        return inited

    def redirect(
        self,
        uri: str,
        method: Literal["GET", "PUT", "POST", "DELETE", "TRACE", "OPTIONS"],
        cl: "Client",  # forward reference to prevent cyclic imports, and preserve intellisense
        **extra,
    ):
        """This is the method you need to use to redirect to the URI that's located in a request with a code of above or equal to 300 and below 400. Automatically sends a request of `method` to `URI`.
        The **extra parameter is to specify data and headers to send to the redirect URI. If you want to send data, a "data" parameter in the **extra parameter is required, and if you want to send headers, then a "headers" parameter in the **extra parameter is required.
        The Response returned is the return result of sending the specified request to the server.
        """
        methods = {
            "GET": cl.get,
            "PUT": cl.put,
            "POST": cl.post,
            "DELETE": cl.delete,
            "TRACE": cl.trace,
            "OPTIONS": cl.options,
        }
        methods[method](path=uri, **extra)
        resp = cl._s.recv(
            65536
        )  # automatic, who cares how much they want to recieve smh
        return self._parse(resp, False)

    def unencode_gzip(self):
        """Unencodes gzip encoded body."""
        # how we're going to do this is to just load the body into memory and decode that memory
        gzip_data = BinaryIO()
        gzip_data.write(self.data)  # type: ignore
        file = gzip.GzipFile(fileobj=gzip_data, mode="rb")
        self.data = file.read()
