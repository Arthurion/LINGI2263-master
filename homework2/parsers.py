import re

# a parser is a function of str, offset, returns (node, length)


def sugar_parser(p):
    def ret_print_parser(format="%s", really=True):
        @sugar_parser
        def parser(str, offset=0):
            n, l = p(str, offset)
            if l < 0:
                return n, l
            print(format % (n,))
            return n, l

        return parser if really else p

    def ret_collector_parser(list):
        @sugar_parser
        def parser(str, offset=0):
            n, l = p(str, offset)
            if l < 0:
                return n, l
            list.append(n)
            return n, l

        return parser

    def ret_replace_parser(node):
        @sugar_parser
        def parser(str, offset=0):
            n, l = p(str, offset)
            if l < 0:
                return n, l
            return node, l

        return parser

    def ret_transform_parser(trans):
        @sugar_parser
        def parser(str, offset=0):
            n, l = p(str, offset)
            if l < 0:
                return n, l
            return trans(n), l

        return parser

    def ret_test_parser(format="%s", *, show=False, forget=True):
        @sugar_parser
        def parser(str, offset=0):
            n, l = p(str, offset)
            if l < 0:
                return n, l
            if show:
                print(format % (n,))
            if forget:
                return None, -1
            return n, l

        return parser

    def ret_not_parser():
        return p_not(p)

    def ret_try_replace(p2):
        @sugar_parser
        def parser(str, offset=0):
            n1, l1 = p(str, offset)
            n2, l2 = p2(str, offset)
            if n1 != n2 or l1 != l2:
                print("orig: %s\nnew : %s\n" % (n1, n2))
            return n1, l1

        return parser

    p.print = ret_print_parser
    p.replace = ret_replace_parser
    p.transform = ret_transform_parser
    p.format = lambda format: p.transform(lambda n: format % (n,))
    p.collect = ret_collector_parser
    p.try_replace = ret_try_replace
    p.test = ret_test_parser
    return p


def p_not(parser):
    @sugar_parser
    def parse(str, offset=0):
        n, l = parser(str, offset)
        if l < 0:
            return None, 0
        return None, -1

    return parse


def p_regex(regex, flags=0):
    """ p_regex returns a parser that matches a regex at the current offset """
    r = re.compile(regex, flags=flags)

    @sugar_parser
    def parse(str, offset=0):
        match = r.match(str, offset)
        if match is None:
            return None, -1
        match = match.group(0)
        return match, len(match)

    return parse


def p_str(s):
    """ p_str returns a parser that matches a string at the current offset """
    @sugar_parser
    def parse(str, offset=0):
        if not str.startswith(s, offset):
            return None, -1
        else:
            return s, len(s)

    return parse


def p_mult(parser, *, separator=p_regex(r'[\t\n ]*'), min_len=0):
    @sugar_parser
    def parse(str, offset=0):
        nodes = []
        length = 0
        wl = 0
        while True:
            n, l = parser(str, offset+length)
            if l < 0:
                length -= wl
                break
            length += l
            nodes.append(n)

            w, wl = separator(str, offset+length)
            if wl < 0:
                break
            length += wl

        if len(nodes) < min_len:
            return None, -1
        return nodes, length

    return parse


def p_opt(parser, node=None):
    """
        p_opt returns an optional parser. That means that if parser doesn't match the string, a default node is returned
    """
    @sugar_parser
    def parse(str, offset=0):
        return node, 0
    return p_or(parser, parse)


_all = object()


def p_and(*parsers, extract=None, keep=_all):
    """
        p_and returns a parser that matches a sequence of parser at the current offset. If one fails, the generated
        parser returns an error.
    """
    @sugar_parser
    def parse(str, offset=0):
        nodes = [None for i in range(0, len(parsers) if keep is _all else len(keep))]
        length = 0
        for i, p in enumerate(parsers):
            (n, l) = p(str, offset+length)
            if l < 0:
                return None, -1

            if keep is _all:
                nodes[i] = n
            elif i in keep:
                nodes[keep.index(i)] = n

            length += l

        return nodes if extract is None else nodes[extract], length

    return parse


def p_phrase(*parsers, extract=None, keep=_all, wp=p_regex(r'[\t\n ]*')):
    """
        p_phrase returns a parser that returns the result of a sequence of parser. Each call to a parser is preceded
        by a call to the wp (whitespace parser). The whitespaces are discarded from the resulting list, and as soon as
        one fails, returns None, -1 (error)
    """
    @sugar_parser
    def parse(str, offset=0):
        nodes = [None for i in range(0, len(parsers) if keep is _all else len(keep))]
        length = 0
        for i, p in enumerate(parsers):
            w, l = wp(str, offset+length)
            if l < 0:
                break
            length += l

            n, l = p(str, offset+length)
            if l < 0:
                return None, -1

            if keep is _all:
                nodes[i] = n
            elif i in keep:
                nodes[keep.index(i)] = n

            length += l

        return nodes if extract is None else nodes[extract], length

    return parse


def p_or(*parsers):
    """
        p_or returns a parser that returns the result of the first successful parser on the given string at the given
        offset
    """
    @sugar_parser
    def parse(str, offset=0):
        for p in parsers:
            (n, l) = p(str, offset)
            if l < 0:
                continue
            return n, l
        return None, -1
    return parse
