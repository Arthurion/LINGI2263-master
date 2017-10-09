import unittest

from train import *


class EqualTesterDictionary:
    def __init__(self, case, f):
        self.case = case
        self.f = f

    def __setitem__(self, key, value):
        self.case.assertEqual(value, self.f(key))


class SimplifyTest(unittest.TestCase):
    def runTest(self):
        simp = EqualTesterDictionary(self, simplify)

        assert simplify('berries') == 'berry'
        assert simplify('bones') == 'bone'
        assert simplify('roses') == 'rose'
        assert simplify('toes') == 'toe'
        assert simplify('gases') == 'gas'

        assert simplify('am') == 'be'
        assert simplify('are') == 'be'
        assert simplify('was') == 'be'
        assert simplify('had') == 'have'
        assert simplify('goes') == 'go'
        assert simplify('paths') == 'path'

        for t in ['this', 'be', 'a', 'municipality', 'in', 'the']:
            assert simplify(t) == t or simplify(t) is None


if __name__ == '__main__':

    unittest.main()
