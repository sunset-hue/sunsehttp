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
        self.mask: int = 0
        """The mask to unmask the data."""
        self.data: bytes = b""
        """The data."""
        self.extended_portion: bytes = b""
        """The extended data portion of the payload, if applicable."""

    def parser(self):
        """parses frame"""
        inted = int(self.parse)
        i = 0
        for n in range(0, inted + 1):
            if inted >> n & 1 and i == 0:
                self.final = True
            if inted >> n & 1 and i == 8:
                self.masked = True
            i += 1
        binary_rep = f"{inted:b}"
        self.opcode = int(binary_rep[4:7], 2)
        # what we're doing here is turning the integer we got into bytes, then getting bits 4 to 8, then turning it into a decimal integer.
        if 0 <= int(binary_rep[9:16], 2) <= 125 and self.masked:
            self.mask = int(
                binary_rep[17:49], 2
            )  # since there's no extra payload length, the extended part of the message is basically empty, so the masking key takes its place (to 49, because the masking key is 32 bit)
            self.data = bytes(
                int(binary_rep[50:]) & self.mask
            )  # unmasks masked bits so we get raw data.
        # now we need to add logic for payloads that are larger than 125 bytes
