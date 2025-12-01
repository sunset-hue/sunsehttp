import socket
from urllib.parse import urlparse, urlunparse, urlencode
from typing import Any, Callable
import ssl

from .util.exceptions import NotAbsoluteUrl
from .util.http_request import Request, Headers, Options, MultipartRequest
from .util.resp import Response
from .util.cookie import Cookie

# multipart so it makes sense:
# put multipart on POST
# PUT
# PATCH
# basically it, since GET, OPTIONS, DELETE, TRACE, and HEAD don't really need this type of modularity


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
        self._s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if not url.endswith("/"):
            self.url = urlparse(url)
        elif ssl:
            raise NotImplementedError("Not implemented as of version 0.1.0.")
        else:
            raise NotAbsoluteUrl(f"{url} is not absolute")
        self.__get_cache = []
        self.cookies: list[Cookie] = []
        """The current cookies that the client has cached for use."""
        self._do_connect(port=80)

    def _do_connect(self, port: int | None = 80):
        "internal"
        self._s.connect(
            (
                f"{urlunparse(self.url)}",
                port,
            )
        )  # null, hopefully this doesn't cause any problems
        return self._s

    def handle_redirects(
        self,
        response: Response | Headers,
        method: str,
        headers: dict[str, Any] | None,
        data: Any | None,
    ):
        methods = {
            "GET": self.get,
            "PUT": self.put,
            "POST": self.post,
            "DELETE": self.delete,
            "TRACE": self.trace,
            "OPTIONS": self.options,
            "HEAD": self.head,
        }
        if isinstance(response, Response):
            if response.code >= 300 < 400:
                match response.code:
                    case 301, 302, 303, 305:
                        response.redirect(
                            response.headers["Location"],  # type: ignore
                            method,  # type: ignore
                            self,
                            data=data,
                            headers=headers,
                        )
                        return
        methods[method](response.location)  # type: ignore

    def get(
        self,
        path: str,
        params: dict | None = None,
        headers: dict[str, int | str] | None = None,
        size: int = 65536,
        strict: bool = False,
        redirects: bool = True,
        unencoder: Callable[..., None] | None = None,
    ):
        """Sends a GET request to `self.url`+*route*.\n
        Note: If you want to supply a cookie through any of the requests, you will have to put it as a header, due to limitations as of 0.1.0. This is going to be fixed in later updates in 0.1.x.
        Args:
            route (str): The path to send the request to.
            params (dict | None): Any query params needed for the request. Defaults to None.
            headers (list[dict] | dict | None): Any headers needed for the request. Needs to be entered as a dict with all the headers you need inside it, in header-value pairs. Defaults to None.
            size (int): The max size that the internal `socket` will retrieve of the incoming request.
            strict (bool): Whether to error out on any HTTP codes greater than 400, with a custom reason. Defaults to `False`.
            redirects (bool): Whether to redirect automatically to the specified resource if a 3xx code is recieved. Defaults to `True`. If this is set to `False`, you will have to handle the follow-up request.
            redirect_op_index (int): The index to use the URI of if a 300 code is recieved. Defaults to 0, meaning the first URI listed. Only valid if redirects is set to `True`, else does nothing. Unused and not a parameter as of 0.1.0bc1.
            unencoder (Callable[[str, bytes],None] | None): The custom unencoder function to use, since sunsehttp only provides support for gzip decompression. The function should take the encoding string as the first parameter, and the request body in bytes as the second one.
        Returns:
            `Response` - The parsed response, with the response body, if applicable.
        """
        s = self._s
        r = Request(
            headers=headers,
            path=f"{path}{urlencode(params) if params else ""}",
            url=urlunparse(self.url),
        ).construct()
        s.send(r)
        r = s.recv(size)
        constructed = Response._parse(r, strict, unencoder)
        if redirects:
            self.handle_redirects(constructed, "GET", headers, None)
        if constructed in self.__get_cache:
            for i in self.__get_cache:
                if constructed == i:
                    return i
        if constructed.headers.get("Set-Cookie"):
            self.cookies.append(
                Cookie({"Set-Cookie": constructed.headers["Set-Cookie"]})
            )
        return constructed

    def post(
        self,
        path: str,
        params: dict | None = None,
        headers: dict[str, int | str] | None = None,
        size: int = 65536,
        strict: bool = False,
        data: Any = None,
        unencoder: Callable[[str, bytes], None] | None = None,
        redirects: bool = True,
    ):
        """Sends a POST request to `self.url`+*route*. \n
        Note: If you want to supply a cookie through any of the requests, you will have to put it as a header, due to limitations as of 0.1.0. This is going to be fixed in later updates in 0.1.x.
        Args:
            route (str): The path to send the request to.
            params (dict | None): Any query params needed for the request. Defaults to None.
            headers (list[dict] | dict | None): Any headers needed for the request. Needs to be entered as a dict with all the headers you need inside it, in header-value pairs. Defaults to None.
            size (int): The max size that the internal `socket` will retrieve of the incoming request. (in bytes)
            strict (bool): Whether to error out on any HTTP codes greater than 400, with a custom reason. Defaults to `False`.
            data (Any): The data to send to the path. Make sure this datatype can be encoded or decoded into `bytes`.
            unencoder (Callable[[str,bytes],bytes] | None): The custom unencoder function to use, since sunsehttp only provides support for gzip decompression. The function should take the encoding string as the first parameter, and the request body in bytes as the second one.
            redirects (bool): Whether to automatically handle redirects (return codes that are 3xx). Defaults to True. If set to False, you will have to handle redirects by yourself. There is a function provided for this in the `Response` class.

        Returns:
            `Response` - The parsed response, with the response body, if applicable.
        """
        s = self._s
        r = Request(
            headers=headers,
            path=f"{path}{urlencode(params) if params else ""}",
            method="POST",
            data=data,
            url=urlunparse(self.url),
        ).construct()
        s.send(r)
        r = s.recv(size)
        res = Response._parse(r, strict, unencoder)
        if redirects:
            res.redirect(res, "POST", self, headers=headers, data=data)  # type: ignore
        h = Response._parse(r, strict, unencoder).headers
        if h.get("Set-Cookie"):
            self.cookies.append(Cookie({"Set-Cookie": h["Set-Cookie"]}))
        return Response._parse(r, strict, unencoder)

    def put(
        self,
        path: str,
        params: dict | None = None,
        headers: dict[str, int | str] | None = None,
        size: int = 65536,
        strict: bool = False,
        data: Any = None,
        unencoder: Callable[[str, bytes], None] | None = None,
        redirects: bool = True,
    ):
        """Sends a PUT request to `self.url`+*route*. \n
        Note: If you want to supply a cookie through any of the requests, you will have to put it as a header, due to limitations as of 0.1.0. This is going to be fixed in later updates in 0.1.x.
        Args:
            route (str): The path to send the request to.
            params (dict | None): Any query params needed for the request. Defaults to None.
            headers (list[dict] | dict | None): Any headers needed for the request. Needs to be entered as a dict with all the headers you need inside it, in header-value pairs. Defaults to None.
            size (int): The max size that the internal `socket` will retrieve of the incoming request. (in bytes)
            strict (bool): Whether to error out on any HTTP codes greater than 400, with a custom reason. Defaults to `False`.
            data (Any): The data to send to the path. Make sure this datatype can be encoded into `bytes`.
            unencoder (Callable[[str,bytes],bytes] | None): The custom unencoder function to use, since sunsehttp only provides support for gzip decompression. The function should take the encoding string as the first parameter, and the request body in bytes as the second one.
            redirects: (bool): Whether to automatically manage redirects (responses with a code of 3xx) or not. Defaults to `True`. If `False`, you will have to manage redirects on your own.
        Returns:
            `Response` - The parsed response, with the response body, if applicable.
        """
        s = self._s
        r = Request(
            headers=headers,
            path=f"{path}{urlencode(params) if params else ""}",
            method="PUT",
            data=data,
            url=urlunparse(self.url),
        ).construct()
        s.send(r)
        r = s.recv(size)
        h = Response._parse(r, strict).headers
        res = Response._parse(r, strict)
        if redirects:
            self.handle_redirects(res, "PUT", headers=headers, data=data)
        if h.get("Set-Cookie"):
            self.cookies.append(Cookie({"Set-Cookie": h["Set-Cookie"]}))
        return Response._parse(r, strict, unencoder)

    def delete(
        self,
        path: str,
        params: dict | None = None,
        headers: dict[str, int | str] | None = None,
        size: int = 65536,
        strict: bool = False,
    ):
        """Sends a DELETE request to `self.url`+*route*.

        Args:
            route (str): The path to send the request to.
            params (dict | None): Any query params needed for the request. Defaults to None.
            headers (list[dict] | dict | None): Any headers needed for the request. Needs to be entered as a dict with all the headers you need inside it, in header-value pairs. Defaults to None.
            size (int): The max size that the internal `socket` will retrieve of the incoming request. (in bytes)
            strict (bool): Whether to error out on any HTTP codes greater than 400, with a custom reason. Defaults to `False`.

        Returns:
            `Response` - The parsed response, with the response body, if applicable.
        """
        s = self._s
        r = Request(
            headers=headers,
            path=f"{path}{urlencode(params) if params else ""}",
            method="DELETE",
            url=urlunparse(self.url),
        ).construct()
        s.send(r)
        r = s.recv(size)
        return Response._parse(r, strict)

    def head(
        self,
        path: str,
        params: dict | None = None,
        headers: dict[str, int | str] | None = None,
        size: int = 65536,
        redirects: bool = True,
    ) -> Headers:
        """Sends a HEAD request to `self.url`+*route*. This is the same as a GET request, but the server only sends the headers of the requested resource.

        Args:
            path (str): The path to send the request to.
            params (dict | None, optional): Any query params needed for the request. Defaults to None.
            headers (dict[str, int  |  str] | None, optional): Any headers needed for the request. Needs to be entered as a dict with all the headers you need inside it, in header-value pairs. Defaults to None.
            size (int, optional): The max size that the internal `socket` will retrieve of the incoming request (in bytes). Defaults to 65536.
            redirects (bool): Whether to automatically manage redirects or not. Defaults to `True`. If `False`, you will have to manually manage redirects.

        Returns:
            Headers: The headers of the resource.
        """
        s = self._s
        r = Request(
            headers=headers,
            path=f"{path}{urlencode(params) if params else ""}",
            method="HEAD",
            url=urlunparse(self.url),
        ).construct()
        s.send(r)
        r = s.recv(size)
        res = Headers().instantiate(r.decode())
        if redirects:
            self.handle_redirects(res, "HEAD", headers=headers, data=None)
        return res

    def options(
        self,
        path: str,
        target: str,
        size: int = 65536,
    ):
        """Sends an OPTIONS request to `self.url`+*route*. This allows the client to view the HTTP request methods that are allowed to be used on this resource.

        Args:
            path (str): The path to send the request to.
            target (str): The target resource to find the operable methods of.
            size (int, optional): The max size that the internal `socket` will retrieve of the incoming request (in bytes). Defaults to 65536.
        Returns:
            Headers: The specific header you need to access to actually retrieve your information on the available HTTP request. The valid HTTP methods are specified in the Allow header, so in this class, it would be `Headers.allow` to access the available methods.
        """
        s = self._s
        r = Options(url=urlunparse(self.url), target=target, path=path).construct()
        s.send(r)
        r = s.recv(size)
        return Headers().instantiate(r.decode())

    def trace(
        self,
        path: str,
        headers: dict[str, int | str] | None = None,
        size: int = 65536,
        error=False,
    ):
        """Sends a TRACE request to `self.url`+*route*. This is like a ping to the server, to verify it's working.

        Args:
            path (str): The path to send the request to.
            headers (dict[str, int | str] | None): The headers you want to send with this request. The headers should be in a dict with every header you need, seperated into header-value pairs. Defaults to None.
            size (int, optional): The max size that the internal `socket` will retrieve of the incoming request (in bytes). Defaults to 65536.
        Returns:
            Response: A response that contains the code, and also contains the headers of this request.
        """
        s = self._s
        r = Request(
            headers=headers, method="TRACE", path=path, url=urlunparse(self.url)
        ).construct()
        s.send(r)
        r = s.recv(size)
        return Response._parse(r, error)
        # for this, we may need more robust parsing due to the data being headers, and we're just using the str constructor

    def patch(
        self,
        path,
        headers: dict[str, int | str] | None = None,
        data: Any = None,
        size: int = 65536,
        error: bool = False,
        unencoder: Callable[[str, bytes], None] | None = None,
        redirects: bool = True,
    ):
        """Sends a PATCH request to `self.url`+*route*.

        Args:
            path (str): The path to send the request to.
            headers (dict[str, int | str] | None): The headers you want to send with this request. The headers should be in a dict with every header you need, separated into header-value pairs. Defaults to None.
            size (int, optional): The max size that the internal `socket` will retrieve of the incoming request (in bytes). Defaults to 65536.
            error (bool): Whether to error out on error codes above 400.
            unencoder (Callable[[str,bytes],bytes] | None): The custom unencoder function to use, since sunsehttp only provides support for gzip decompression. The function should take the encoding string as the first parameter, and the request body in bytes as the second one.
            redirects (bool): Whether to automatically perform redirects if needed. Defaults to True. If set to False, you will have to handle redirects yourself.
        Returns:
            Response: A response that contains the code, and also contains the headers of this request.
        """
        s = self._s
        r = Request(
            headers=headers,
            method="PATCH",
            path=f"{path}",
            data=data,
            url=urlunparse(self.url),
        ).construct()
        s.send(r)
        r = s.recv(size)
        if redirects:
            self.handle_redirects(
                Response._parse(r, error, unencoder), "PATCH", headers, data
            )
        return Response._parse(r, error, unencoder)

    def multipart_post(self, requests: list[Request] | MultipartRequest): ...


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
        self._s = self.__context.wrap_socket(
            socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        )
        if not url.endswith("/"):
            self.url = urlparse(url)
        else:
            raise NotAbsoluteUrl(f"{url} is not absolute")
        self.__get_cache = []
        self._do_connect(port=443)
