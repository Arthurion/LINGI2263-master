from train import *
import fractions
from estimation import *
import math

with Timer("--- Loading the test file"):
    with open('definitions_test.txt', encoding='utf8') as f:
        lines = [l for l in f.readlines() if only_commas.match(l) is None]

with Timer("--- Tokenizing it") as timer:

    tokens = [None] * len(lines)
    for i, line in enumerate(lines):
        tokens[i] = tokenizer(line)[0]
        timer.progress(100*i//len(lines))

num = 0
deno = 0
with Timer("--- Removing unknown tokens and merging case, plurals, verbs, ..."):
    for i, line in enumerate(tokens):
        for j, token in enumerate(line):
            deno += 1
            simp = simplify(token.lower())
            if lexicon.get(simp, 0) != 0:
                tokens[i][j] = simp
            elif lexicon.get(token.lower(), 0) != 0:
                tokens[i][j] = token.lower()
            elif lexicon.get(token, 0) == 0:
                tokens[i][j] = '<UNK>'
                num += 1

print("OOV rate: %.2f%%" % (100*num/deno,))

methods = [
    ('Laplace 1', laplace_prob, 1),
    ('Laplace 2', laplace_prob, 2),
    ('Laplace 3', laplace_prob, 3),
    ('Laplace 4', laplace_prob, 4),
    ('Laplace 5', laplace_prob, 5),
    ('Backoff 1', backoff_prob, 1),
    ('Backoff 2', backoff_prob, 2),
    ('Backoff 3', backoff_prob, 3),
    ('Backoff 4', backoff_prob, 4),
    ('Backoff 5', backoff_prob, 5),
]
for s, prob, n in methods:
    with Timer("--- Computing the perplexity for %s" % (s,)) as timer:
        ngram_stack = []
        ngram = collections.deque()
        total = len(tokens)
        per_symbol_ll = 0
        words = 0
        for i, line in enumerate(tokens):
            words += len(line)
            last = None
            for j, token in enumerate(line):
                # enter an inner context
                if token == '(':
                    ngram_stack.append(copy.copy(ngram))
                    ngram.clear()

                # now, feed the word
                ngram.append(token)
                if token == '<s>':  # skip if a <s>, completely predictable
                    continue
                if len(ngram) > n:
                    ngram.popleft()
                pr = prob(len(ngram), tuple(ngram))
                per_symbol_ll += math.log2(pr)

                # leave an inner context
                if token == ')' and len(ngram_stack) > 0:
                    ngram = ngram_stack.pop()
                if token == '</s>':
                    ngram.clear()

            ngram.clear()
            timer.progress(100*i//total)
        print(2**(-per_symbol_ll/words))
