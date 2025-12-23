import socket
from urllib.parse import urlencode
import ssl
import base64
import hashlib


from ..http.http_request import Request
from ..http.resp import Response
from ..http.exceptions import NotAbsoluteUrl, ImproperWebsocketCode, WsHandshakeFailed
from .frame import SocketFrame


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
        self.sha_1: str | None  = "" 
        self.do_connect()

    def do_connect(self):
        if self.uri.startswith("http") or self.uri.startswith("ws://"):
            self._s.connect((self.uri, 80))
        else:
            self._s.connect((self.uri, 443))
        # below is the starting handshake
        s = self._s
        self.__expectedkey = base64.standard_b64encode(hashlib.sha1(b"websockkey" + b"258EAFA5-E914-47DA-95CA-C5AB0DC85B1").digest())
        r = Request(
            self.uri,
            headers={"Host": self.uri, "Upgrade": "websocket", "Connection": "Upgrade","Sec-Websocket-Version": 13, "Sec-Websocket-Key": str(base64.b64encode(b"websockkey"))},
            method="GET",
        ).construct()  # starting handshake
        res = Response._parse(s.recv(65536), False)
        self.sha_1 = res.headers.get("Sec-Websocket-Accept") # pyright: ignore[reportAttributeAccessIssue]
        if res.code != 101:
            raise ImproperWebsocketCode(
                f"{self.uri} sent an invalid handshake code of {res.code}, instead of 101 - Switching Protocols."
            )
        if res.headers.get("Upgrade") is None or res.headers.get("Upgrade").lower() != "websocket":  # type: ignore
            raise WsHandshakeFailed("Websocket handshake failed due to no Upgrade header provided by the server, or the Upgrade header specifying the wrong protocol.")
        if res.headers.get("Connection") is None or res.headers.get("Connection").lower() != "Upgrade" # type: ignore
            raise WsHandshakeFailed("Websocket handshake failed due to missing or malformed Connection header.")
        if self.sha_1 is None or self.sha_1 != self.__expectedkey:
            raise WsHandshakeFailed("Websocket server failed to send SHA-1 string, or SHA-1 string was malformed.")
        if res.headers.get("Sec-Websocket-Protocol"): # we haven't defined any protocol at all
            raise WsHandshakeFailed("Websocket server requested a subprotocol that was not indicated by the client handshake.")
    
    def send(self, msg: bytes | str, path: str = "/", queries: dict | None = None, encoding: str = "utf-8", size: int = 65536) -> SocketFrame:
        """Sends a websocket message to `self.url` + `path`

        Args:
            msg (bytes | str): The message to send to the websocket server.
            path (str, optional): The path at which to send a message to. Defaults to "/".
            queries (dict, optional): The queries for the path. Defaults to None.
        
        Returns:
            `SocketFrame`: The parsed socket response. (Has limitations to what sunsehttp can recieve as of 0.1.0.)
        """
        with self._s as s:
            old = self.uri
            self.uri = old + path + urlencode(queries) # type: ignore
            s.send(bytes(msg, encoding="utf-8") if isinstance(msg, str) else msg)
            rec = s.recv(size)
            self.uri = old
            return SocketFrame(rec)
