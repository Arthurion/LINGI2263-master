from train import *
from estimation import *
import random

with Timer("--- Loading the test file"):
    with open('definitions_test.txt', encoding='utf8') as f:
        lines = [l for l in f.readlines() if only_commas.match(l) is None]

with Timer("--- Tokenizing it") as timer:

    tokens = [None] * len(lines)
    for i, line in enumerate(lines):
        tokens[i] = tokenizer(line)[0]
        timer.progress(100*i//len(lines))

with Timer("--- Removing unknown tokens and merging cases"):
    for i, line in enumerate(tokens):
        for j, token in enumerate(line):
            simp = simplify(token.lower())
            if lexicon.get(simp, 0) != 0:
                tokens[i][j] = simp
            elif lexicon.get(token.lower(), 0) != 0:
                tokens[i][j] = token.lower()
            elif lexicon.get(token, 0) == 0:
                tokens[i][j] = '<UNK>'


def histories(n=3):
    hist = collections.deque()
    while True:
        line = random.choice(tokens)
        print(' '.join(line))
        for token in line:
            hist.append(token)
            if len(hist) >= n:
                hist.popleft()
            yield tuple(hist)


def verify(prob_fct, n, hist):
    """Verifying ∀h sum P(w|h) = 1
    """
    sum = 0
    for w in lexicon:
        sum += prob_fct(n, hist+(w,))
    if abs(sum - 1) > 1e-8:
        raise Exception('bad probabilities for n=%d: %f' % (n, sum))

with Timer("--- Testing on unencountered data", prg="%d histories tested") as timer:
    for i, hist in enumerate([(), ('<1>',), ('<1>', '<2>'), ('<1>', '<2>', '<3>'), ('<1>', '<2>', '<3>', '<4>')]):
        verify(backoff_prob, len(hist)+1, hist)
        timer.progress(i/10)
    # Mixing known and unknown
    for i, hist in enumerate([(), ('<1>',), ('<1>', 'be'), ('<1>', '<2>', 'is'), ('<1>', 'a', '<3>', 'of')]):
        verify(backoff_prob, len(hist)+1, hist)
        timer.progress(i/10)

with Timer("--- Testing on random data", prg="%d histories tested") as timer:
    hists = histories(5)
    for i, hist in enumerate(hists):
        verify(backoff_prob, len(hist)+1, hist)
        timer.progress(i+1)