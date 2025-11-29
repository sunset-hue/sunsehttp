class Cookie:
    """Represents a Cookie sent through the Set-Cookie header that a server sends as a response. Cookies are small bits of data that a server sends to a client that may be used for authentication and purposes that relate to that.
    This can be used as a server application."""

    def __init__(self, cookie_header: dict[str, str]):
        """Constructs a cookie.

        Args:
            string (str, optional): This should be the header that the client recieves from the `Set-Cookie` header. Usually, if you are a client, this class is already instantiated for you. Defaults to "".
        """
        self.raw_data = cookie_header
        self.data: str = ""
        """The data that's provided in the cookie pair, an octet. (RFC 6265)"""
        self.cookie_name: str = ""
        """The name of the cookie."""
        self.expires: str = ""
        """The expiring date of the cookie. The valid date formats are defined according to RFC 2616, Section 2.2."""
        self.max_age: str = ""
        """The max age that this cookie can be. The valid date formats are defined according to RFC 2616, Section 2.2."""
        self.domain: str = ""
        """The subdomain of this cookie, as defined in RFC 1034, Section 3.5, and as enhanced in RFC 1123, Section 2.1."""
        self.path: str = ""
        """The scope of which this cookie is valid/authenticates for. If specified, any other paths that are not said here that are accessed with this cookie will be forbidden/not accessible."""
        self.secure: bool = False
        """If this is specified, this cookie only transmits on secure channels such as HTTPS. If specified, this value should be `True`, else it should always be `False`."""
        self.http_only: bool = False
        """If this is specified, this cookie cannot be accessed to third party scripts such as scripts made by JavaScript. If specified, this value should be `True`, else `False`."""
        self.extra: str = ""
        """If specified, contains extra metadata associated with the cookie, which can be useful for certain situations in authentication."""

    def parse(self):
        """Parses the cookie data to the attributes specified in this class. If any attribute has a value of an empty string, assume that that content was not available in the raw data."""
