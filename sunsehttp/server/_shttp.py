"""Contains the server-side function definitions."""


class Server:
    def __init__(self, url: str = "localhost", port: int | None = None):
        self.url = url + str(port) if port else ""
        self.__map = {"/": "GET"}  # the paths that are defined within this server

    def start(self):
        """Starts the server and allows the server to respond to requests."""
