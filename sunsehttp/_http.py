import socket
from urllib.parse import urlparse, urlencode, urlunparse
from typing import TYPE_CHECKING, Any
import ssl

from .util.exceptions import NotAbsoluteUrl
from .util.http_request import Request, Headers, Options
from .util.resp import Response


class Client:
    """A HTTP client that allows you to use HTTP methods on a specific url, or more if needed.
    This client is the base class of SslClient. This class has an option to use SSL while connecting, but if it's not supplied explicitly, it assumes that no secure connection is needed, and defaults to HTTP, instead of HTTPS.
    """

    def __init__(self, url: str, ssl: None = None):
        """Creates an instance of `Client`, that operate on `url`, and may use SSL (NOT IMPLEMENTED AS OF NOW)

        Args:
            url (str): The URL of the website you want this client to send and receive requests from.
            ssl (None, optional): Not Implemented. Defaults to None.

        Raises:
            NotAbsoluteUrl: Raised if the url supplied is not absolute.
        """
        self.__s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if not url.endswith("/") and url.startswith("www."):
            self.url = urlparse(url)
        elif ssl:
            raise NotImplementedError("Not implemented as of version 0.1.0.")
        else:
            raise NotAbsoluteUrl(f"{url} is not absolute")
        self.__get_cache = []

    def _do_connect(self, port: int | None = 80):
        "internal"
        self.__s.connect(
            (
                f"{urlunparse(self.url)}",
                port,
            )
        )  # null, hopefully this doesn't cause any problems
        return self.__s

    def get(
        self,
        path: str,
        params: dict | None = None,
        headers: dict[str, int | str] | None = None,
        port: int | None = 80,
        size: int = 65536,
        strict: bool = False,
        constructor: type = type[str],
    ):
        """Sends a GET request to `self.url`+*route*.

        Args:
            route (str): The path to send the request to.
            params (dict | None): Any query params needed for the request. Defaults to None.
            headers (list[dict] | dict | None): Any headers needed for the request. Needs to be entered as a dict with all the headers you need inside it, in header-value pairs. Defaults to None.
            port (int | None): The port to connect to on the specified url. Defaults to 80, for HTTP connections on this client class.
            size (int): The max size that the internal `socket` will retrieve of the incoming request.
            strict (bool): Whether to error out on any HTTP codes greater than 400, with a custom reason. Defaults to `False`.
            constructor (type): The type to construct the data of the response to. Defaults to the type of bytes.

        Returns:
            `Response` - The parsed response, with the response body, if applicable.
        """
        with self._do_connect(port) as s:
            r = Request(
                headers=headers,
                path=f"{path}{urlencode(params) if params else ""}",
                url=urlunparse(self.url),
            ).construct()
            s.send(r)
            r = s.recv(size)
            if Response()._parse(r, strict, constructor) in self.__get_cache:
                for i in self.__get_cache:
                    if Response()._parse(r, strict, constructor) == i:
                        return i
            return Response()._parse(r, strict, constructor)

    def post(
        self,
        path: str,
        params: dict | None = None,
        headers: dict[str, int | str] | None = None,
        port: int | None = 80,
        size: int = 65536,
        strict: bool = False,
        data: Any = None,
        constructor: type = type[str],
    ):
        """Sends a POST request to `self.url`+*route*.

        Args:
            route (str): The path to send the request to.
            params (dict | None): Any query params needed for the request. Defaults to None.
            headers (list[dict] | dict | None): Any headers needed for the request. Needs to be entered as a dict with all the headers you need inside it, in header-value pairs. Defaults to None.
            port (int | None): The port to connect to on the specified url. Defaults to 80, for HTTP connections on this client class.
            size (int): The max size that the internal `socket` will retrieve of the incoming request. (in bytes)
            strict (bool): Whether to error out on any HTTP codes greater than 400, with a custom reason. Defaults to `False`.
            constructor (type): The type to construct the data of the response to. Defaults to the type of bytes.
            data (Any): The data to send to the path. Make sure this datatype can be encoded or decoded into `bytes`.

        Returns:
            `Response` - The parsed response, with the response body, if applicable.
        """
        with self._do_connect(port) as s:
            r = Request(
                headers=headers,
                path=f"{path}{urlencode(params) if params else ""}",
                method="POST",
                data=data,
                url=urlunparse(self.url),
            ).construct()
            s.send(r)
            r = s.recv(size)
            return Response()._parse(r, strict, constructor)

    def put(
        self,
        path: str,
        params: dict | None = None,
        headers: dict[str, int | str] | None = None,
        port: int | None = 80,
        size: int = 65536,
        strict: bool = False,
        data: Any = None,
        constructor: type = type[str],
    ):
        """Sends a PUT request to `self.url`+*route*.

        Args:
            route (str): The path to send the request to.
            params (dict | None): Any query params needed for the request. Defaults to None.
            headers (list[dict] | dict | None): Any headers needed for the request. Needs to be entered as a dict with all the headers you need inside it, in header-value pairs. Defaults to None.
            port (int | None): The port to connect to on the specified url. Defaults to 80, for HTTP connections on this client class.
            size (int): The max size that the internal `socket` will retrieve of the incoming request. (in bytes)
            strict (bool): Whether to error out on any HTTP codes greater than 400, with a custom reason. Defaults to `False`.
            constructor (type): The type to construct the data of the response to. Defaults to the type of bytes.
            data (Any): The data to send to the path. Make sure this datatype can be encoded into `bytes`.

        Returns:
            `Response` - The parsed response, with the response body, if applicable.
        """
        with self._do_connect(port) as s:
            r = Request(
                headers=headers,
                path=f"{path}{urlencode(params) if params else ""}",
                method="PUT",
                data=data,
                url=urlunparse(self.url),
            ).construct()
            s.send(r)
            r = s.recv(size)
            return Response()._parse(r, strict, constructor)

    def delete(
        self,
        path: str,
        params: dict | None = None,
        headers: dict[str, int | str] | None = None,
        port: int | None = 80,
        size: int = 65536,
        strict: bool = False,
        constructor: type = type[str],
    ):
        """Sends a DELETE request to `self.url`+*route*.

        Args:
            route (str): The path to send the request to.
            params (dict | None): Any query params needed for the request. Defaults to None.
            headers (list[dict] | dict | None): Any headers needed for the request. Needs to be entered as a dict with all the headers you need inside it, in header-value pairs. Defaults to None.
            port (int | None): The port to connect to on the specified url. Defaults to 80, for HTTP connections on this client class.
            size (int): The max size that the internal `socket` will retrieve of the incoming request. (in bytes)
            strict (bool): Whether to error out on any HTTP codes greater than 400, with a custom reason. Defaults to `False`.
            constructor (type): The type to construct the data of the response to. Defaults to the type of bytes.

        Returns:
            `Response` - The parsed response, with the response body, if applicable.
        """
        with self._do_connect(port) as s:
            r = Request(
                headers=headers,
                path=f"{path}{urlencode(params) if params else ""}",
                method="DELETE",
                url=urlunparse(self.url),
            ).construct()
            s.send(r)
            r = s.recv(size)
            return Response()._parse(r, strict, constructor)

    def head(
        self,
        path: str,
        params: dict | None = None,
        headers: dict[str, int | str] | None = None,
        port: int | None = 80,
        size: int = 65536,
    ) -> Headers:
        """Sends a HEAD request to `self.url`+*route*. This is the same as a GET request, but the server only sends the headers of the requested resource.

        Args:
            path (str): The path to send the request to.
            params (dict | None, optional): Any query params needed for the request. Defaults to None.
            headers (dict[str, int  |  str] | None, optional): Any headers needed for the request. Needs to be entered as a dict with all the headers you need inside it, in header-value pairs. Defaults to None.
            port (int | None, optional): The port to connect to on the specified URL. Defaults to 80, for HTTP connections.
            size (int, optional): The max size that the internal `socket` will retrieve of the incoming request (in bytes). Defaults to 65536.

        Returns:
            Headers: The headers of the resource.
        """
        with self._do_connect(port) as s:
            r = Request(
                headers=headers,
                path=f"{path}{urlencode(params) if params else ""}",
                method="HEAD",
                url=urlunparse(self.url),
            ).construct()
            s.send(r)
            r = s.recv(size)
            return Headers().instantiate(r.decode())

    def options(
        self,
        path: str,
        target: str,
        port: int | None = 80,
        size: int = 65536,
    ):
        """Sends an OPTIONS request to `self.url`+*route*. This allows the client to view the HTTP request methods that are allowed to be used on this resource.

        Args:
            path (str): The path to send the request to.
            target (str): The target resource to find the operable methods of.
            port (int | None, optional): The port to connect to on the specified URL. Defaults to 80, which is the default for HTTP connections.
            size (int, optional): The max size that the internal `socket` will retrieve of the incoming request (in bytes). Defaults to 65536.
        Returns:
            Headers: The specific header you need to access to actually retrieve your information on the available HTTP request methods are specified in the Allow header, so in this class, it would be `Headers.allow`
        """
        with self._do_connect(port) as s:
            r = Options(urlunparse(self.url), target, path).construct()
            s.send(r)
            r = s.recv(size)
            return Headers().instantiate(r.decode())

    def trace(
        self,
        path: str,
        port: int | None = 80,
        headers: dict[str, int | str] | None = None,
        size: int = 65536,
        error=False,
    ):
        """Sends a TRACE request to `self.url`+*route*. This is like a ping to the server, to verify it's working.

        Args:
            path (str): The path to send the request to.
            port (int | None, optional): The port to connect to on the specified URL. Defaults to 80, which is the default for HTTP connections.
            headers (dict[str, int | str] | None): The headers you want to send with this request. The headers should be in a dict with every header you need, seperated into header-value pairs. Defaults to None.
            size (int, optional): The max size that the internal `socket` will retrieve of the incoming request (in bytes). Defaults to 65536.
        Returns:
            Response: A response that contains the code, and also contains the headers of this request.
        """
        with self._do_connect(port) as s:
            r = Request(
                headers=headers, method="TRACE", path=path, url=urlunparse(self.url)
            ).construct()
            s.send(r)
            r = s.recv(size)
            return Response()._parse(r, error, str)
            # for this, we may need more robust parsing due to the data being headers, and we're just using the str constructor

    def patch(
        self,
        path,
        port: int | None = 80,
        headers: dict[str, int | str] | None = None,
        data: Any = None,
        size: int = 65536,
        error: bool = False,
    ):
        """Sends a PATCH request to `self.url`+*route*.

        Args:
            path (str): The path to send the request to.
            port (int | None, optional): The port to connect to on the specified URL. Defaults to 80, which is the default for HTTP connections.
            headers (dict[str, int | str] | None): The headers you want to send with this request. The headers should be in a dict with every header you need, seperated into header-value pairs. Defaults to None.
            size (int, optional): The max size that the internal `socket` will retrieve of the incoming request (in bytes). Defaults to 65536.
            error (bool): Whether to error out on error codes above 400.
        Returns:
            Response: A response that contains the code, and also contains the headers of this request.
        """
        with self._do_connect(port) as s:
            r = Request(
                headers=headers,
                method="PATCH",
                path=f"{path}",
                data=data,
                url=urlunparse(self.url),
            ).construct()
            s.send(r)
            r = s.recv(size)
            return Response()._parse(r, error, str)


class SslClient(Client):
    """A subclass of Client that adds support for HTTPS connections, which use TLS (encrypted data) instead of the cleartext that HTTP uses. If not specified, this process is done for you. This is the client that's recommended to be used most of the time, due to the safety."""

    def __init__(self, url: str):
        """Creates an instance of `Client`, that operate on `url`, that uses HTTPS connections.

        Args:
            url (str): The URL of the website you want this client to send and receive requests from.

        Raises:
            NotAbsoluteUrl: Raised if the url supplied is not absolute.
        """
        super().__init__(url)
        self.__context = ssl._create_default_https_context(ssl.Purpose.CLIENT_AUTH)
        self.__s = self.__context.wrap_socket(
            socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        )
        if not url.endswith("/"):
            self.url = urlparse(url)
        else:
            raise NotAbsoluteUrl(f"{url} is not absolute")
        self.__get_cache = []
