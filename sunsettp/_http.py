import socket
from urllib.parse import urlparse, urlencode
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from util.exceptions import NotAbsoluteUrl


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
        if urlparse(url).netloc and urlparse(url).scheme:
            self.url = urlparse(url)
        elif ssl:
            raise NotImplementedError("Not implemented as of version 0.1.0.")
        else:
            raise NotAbsoluteUrl(f"{url} is not absolute")

    def _do_bind(self, path: str, params: dict | None, port: int | None = 80):
        "internal"
        with self.__s as s:
            s.bind(
                (f"{self.url}{path}{urlencode(params) if params else "\0"}", port)
            )  # null, hopefully this doesn't cause any problems
            return s

    def get(
        self,
        path: str,
        params: dict | None = None,
        headers: list[dict] | dict | None = None,
        port: int | None = 80,
    ):
        """Sends a get request to `self.url`+*route*, with corresponding data if needed.

        Args:
            route (str): The path to send the request to.
            params (dict | None): Any query params needed for the request. Defaults to None.
            headers (list[dict] | dict | None): Any headers needed for the request. Defaults to None.
            port (int | None): The port to connect to on the specified url. Defaults to 80, for HTTP connections on this client class.
        """
        with self._do_bind(path, params, port) as s:
            ...
