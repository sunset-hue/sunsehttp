"""Contains the server-side function definitions."""

from typing import Callable


class Server:
    def __init__(self, url: str = "localhost", port: int | None = None):
        self.url = url + str(port) if port else ""
        self.__map: dict[str, tuple[str, Callable] | str] = {
            "/": "GET"
        }  # the paths that are defined within this server

    def start(self):
        """Starts the server and allows the server to respond to requests."""

    def route(self, path: str, method: str, func: Callable):
        """Creates a route to access a certain resource. Function should contain a ServerResponse class as a return value.
        Args:
            path - str - The path that this resource can be accessed by.
            method - str - The HTTP method that this resource can be accessed by. Non-standard HTTP methods are not supported.
        """

        def adds(**kwargs):
            self.__map[path] = (method, func)

        return adds
