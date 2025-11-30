"""# sunsehttp \n A http library made for fun"""

from .util.constants import error_code_reasons
from .util.exceptions import *
from .util.http_request import Request, Options, Headers
from .util.resp import Response
from ._http import SslClient, Client


# TODO:
# encoding and response parsing
# redirection management
# multipart requests and also file uploading
# websockets impl
# server-side implementation
# more features for QoL or code quality improvement
