import socket
from urllib.parse import urlparse
import ssl


from ..util.http_request import Request
from ..util.resp import Response
from ..util.exceptions import NotAbsoluteUrl, ImproperWebsocketCode, WsHandshakeFailed


class Websocket:
    """Represents a websocket connection."""

    def __init__(self, uri: str):
        """Initiates a websocket connection with `uri`.

        Args:
            uri (str): The URI of the websocket server. Valid protocols to start with are https, wss, http, and ws.
        """
        self.__default_context = ssl.create_default_context()
        self._s = (
            socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if any([self.uri.startswith("http://"), self.uri.startswith("ws://")])
            else self.__default_context.wrap_socket(
                socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            )
        )
        if not uri.endswith("/"):
            self.uri = uri
        else:
            NotAbsoluteUrl("%s is not an absolute url" % self.uri)
        self.do_connect()

    def do_connect(self):
        if self.uri.startswith("http") or self.uri.startswith("ws://"):
            self._s.connect((self.uri, 80))
        else:
            self._s.connect((self.uri, 443))
        # below is the starting handshake
        s = self._s
        r = Request(
            self.uri,
            headers={"Host": self.uri, "Upgrade": "websocket", "Connection": "Upgrade"},
            method="GET",
        ).construct()  # starting handshake
        res = Response._parse(s.recv(65536), False)
        if res.code != 101:
            raise ImproperWebsocketCode(
                f"{self.uri} sent an invalid handshake code of {res.code}, instead of 101 - Switching Protocols."
            )
        if res.headers.get("Upgrade") is None or res.headers.get("Upgrade").lower() != "websocket":  # type: ignore
            raise WsHandshakeFailed("Websocket handshake failed due to no Upgrade header provided by the server, or the Upgrade header specifying the wrong protocol.")
        if res.headers.get("Connection") is None or res.headers.get("Connection").lower() != "Upgrade" # type: ignore
            raise WsHandshakeFailed("Websocket handshake failed due to missing or malformed Connection header.")
        
