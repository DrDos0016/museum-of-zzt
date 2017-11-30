class ParseError(Exception):
    def __init__(self, arg):
        self.msg = arg

class URLError(Exception):
    def __init__(self, arg):
        self.msg = arg
