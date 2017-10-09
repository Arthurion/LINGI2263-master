import time


def static_var(**kwargs):
    def decorate(f):
        for k in kwargs:
            setattr(f, k, kwargs[k])
        return f
    return decorate


@static_var(not_interned=object())
def intern(sym, dic):
    interned = dic.get(sym, intern.not_interned)
    if interned is intern.not_interned:
        dic[sym] = sym
        return sym
    return interned


class Timer(object):
    def __init__(self, message, precision=1, prg="%.2f%%"):
        self.time = None
        self.p = -1
        self.message = message
        self.precision = precision
        self.prg = '%s ... (%s in %s)' % (message, prg, "%.2f seconds")
        print('%s ...' % (message,), end="\r")

    def __enter__(self):
        self.time = time.time()
        return self

    def progress(self, p):
        if p >= self.p + self.precision:
            self.p = p
            print(self.prg % (p, time.time()-self.time), end="\r")

    def __exit__(self, exc_type, exc_val, exc_tb):
        print('%s in %f seconds' % (self.message, time.time()-self.time,))

