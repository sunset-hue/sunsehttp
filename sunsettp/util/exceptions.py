class NotAbsoluteUrl(Exception):
    def __init__(self, *args):
        self.args = args


class Limitation(Exception):
    def __init__(self, *args):
        self.args = args
