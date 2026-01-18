class ServerResponse:
    """The object that should be used when creating a response to a request for a resource."""

    def __init__(
        self, response: str | bytes | None, error: bool = False, code: int = 200
    ):
        """Creates the server response, with an error code if necessary.

        Args:
            response (str | bytes | None): The response to send to the requested clients.
            error (bool, False): Whether to send this response with an error code.
            code (int, 200): The code to send with the response. Defaults to 200 (OK).
        """
        self.response = response
        self.error = error
        self.code = code
