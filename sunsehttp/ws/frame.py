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


class SocketFrame:
    """Represents a message either sent by the client or server. Only servers or methods are recommended to use this class."""

    def __init__(self, frame: bytes):
        self.parse = frame
        self.final: bool = False
        self.opcode: int = 0

    def a(): ...
