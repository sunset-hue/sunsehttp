class NotAbsoluteUrl(Exception):
    def __init__(self, *args):
        self.args = args


class Limitation(Exception):
    def __init__(self, *args):
        self.args = args


class ContinuationWarning(Warning):
    def __init__(self, *args):
        self.args = args


class ClientError(Exception):
    def __init__(self, *args):
        self.args = args
        self.reason: str = ""


class ImproperWebsocketCode(Exception):
    def __init__(self, *args):
        self.args = args


class WsHandshakeFailed(Exception):
    def __init__(self, *args):
        self.args = args
