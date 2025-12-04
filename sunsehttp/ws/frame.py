import enum


class FrameOpcodes(enum.Enum):
    CONTINUE = 0
    TEXT = 1
    BIN = 2
    CLOSE = 8
    PING = 9
    PONG = 10


class ClosureCodes(enum.Enum):
    NORMAL_CLOSURE = 1000
    GOING_AWAY = 1001
    PROTOCOL_ERROR = 1002
    UNACCEPTABLE = 1003
    NOT_CONSISTENT_DATA = 1007
    POLICY_VIOLATION = 1008
    MESSAGE_TOO_BIG = 1009
    MISSING_EXTENSION = 1010
    UNEXPECTED = 1011


class SocketFrame:
    """Represents a message either sent by the client or server. Only servers or methods are recommended to use this class."""

    def __init__(self, frame: bytes):
        self.parse = frame
        self.final: bool = False
        """Whether this message was the final message sent by the websocket server."""
        self.opcode: int = 0
        """The opcode of this message."""
        self.masked: bool = False
        """Whether this frame's data is masked."""
        self.mask: bytes = b""
        """The mask to unmask the data."""
        self.data: bytes = b""

    def parser(self):
        """parses bytes and returns"""
