import re

# a parser is a function of str, offset, returns (node, length)


def p_opt(parser,node=None):
    """ p_opt returns an optional parser. That means that if parser doesn't match the string, a default node is returned """
    def parse(str, offset):
        return node, 0
    return p_or(parser, parse)


def p_regex(regex, flags=0):
    """ p_regex returns a parser that matches a regex at the current offset """
    r = re.compile(regex, flags=flags)

    def parse(str, offset):
        match = r.match(str, offset)
        if match is None:
            return None, -1
        match = match.group(0)
        return match, len(match)

    return parse


def p_str(s):
    """ p_str returns a parser that matches a string at the current offset """
    def parse(str, offset):
        if not str.startswith(s, offset):
            return None, -1
        else:
            return s, len(s)

    return parse


def p_and(*parsers):
    """
        p_and returns a parser that matches a sequence of parser at the current offset. If one fails, the generated
        parser returns an error.
    """
    def parse(str, offset):
        nodes = []
        length = 0
        for p in parsers:
            (n, l) = p(str, offset+length)
            if l < 0:
                return None, -1
            length += l
            nodes.append(n)
        return nodes, length

    return parse


class _Phrase():
    def __init__(self, *parsers, wp):
        self.parsers = parsers
        self.wp = wp

    def __call__(self, str, offset):
        nodes = []
        length = 0
        for p in self.parsers:
            w, l = self.wp(str, offset+length)
            if l < 0:
                break
            length += l

            n, l = p(str, offset+length)
            if l < 0:
                return None, -1
            nodes.append(n)
            length += l

        return nodes, length


def p_phrase(*parsers, wp=p_regex(r'[\t\n ]*')):
    """
        p_phrase returns a parser that returns the result of a sequence of parser. Each call to a parser is preceded
        by a call to the wp (whitespace parser). The whitespaces are discarded from the resulting list, and as soon as
        one fails, returns None, -1 (error)
    """
    return _Phrase(*parsers, wp=wp)


def p_or(*parsers):
    """
        p_or returns a parser that returns the result of the first successful parser on the given string at the given
        offset
    """
    def parse(str, offset):
        for p in parsers:
            (n, l) = p(str, offset)
            if l < 0:
                continue
            return n, l
        return None, -1
    return parse
