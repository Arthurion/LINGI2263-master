import matplotlib.pyplot as plt
from train import *

with Timer("--- Loading N-Grams"):

    ngrams = pickle.load(open('ngrams', 'rb'))


def counts_dist(dic):
    """Computes the count distribution in a dictionary of frequencies.
    """
    counts = collections.defaultdict(lambda: 0)
    for t in dic:
        counts[dic[t]] += 1
    return [c for c in counts], [counts[c] for c in counts]

# Plot the distributions
mls = []
for n, color in zip(ngrams.dicts, ['blue', 'green', 'red', 'cyan', 'yellow']):
    x, y = counts_dist(ngrams.dicts[n])
    mls.append(plt.stem(x, y))
    plt.setp(mls[-1], 'color', color)
    plt.xscale('log')
    plt.yscale('log')

plt.legend(mls, ['%d-Grams' % (n,) for n in ngrams.dicts])
plt.xlabel('Number of occurences')
plt.ylabel('Number of N-grams with such occurences')

print(ngrams)

plt.show()
