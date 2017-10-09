from train import *
import bisect
import math

with Timer("--- Loading N-Grams"):
    with open('lexicon', 'rb') as f:
        lexicon = pickle.load(f)
    with open('ngrams', 'rb') as f:
        ngrams = pickle.load(f)

dicts = ngrams.dicts    # dicts[n][hw] contains the occurrences of every n-gram C(h, w)
hists = {}              # hists[n][h] contains the occurrences of every history C(h)
preds = {}              # preds[n][h][w] contains the occurrences of every history C(w|h)

with Timer("--- Building histories and predictions counts from n-grams"):

    for n in dicts:
        dic = dicts[n]
        hist = collections.defaultdict(lambda: 0)
        pred = collections.defaultdict(lambda: {})
        hists[n] = hist
        preds[n] = pred
        for ngram in dic:
            hist[ngram[:-1]] += dic[ngram]
            pred[ngram[:-1]][ngram[-1]] = dic[ngram]


def prob(n, hw):
    """Basic probability P(w|h), without smoothing"""
    return dicts[n][hw] / hists[n].get(hw[:-1], 0)


def laplace_prob(n, hw):
    """Laplace probability P(w|h), introducing a very simple smoothing"""
    return (dicts[n].get(hw, 0) + 1) / (hists[n].get(hw[:-1], 0) + len(lexicon))


# We are going to compute the maximal d_c, a parameter for the backoff smoothing
with Timer("--- Computing d_c"):
    n1 = 0
    n2 = 0
    for n in dicts:
        for ngram in dicts[n]:
            if dicts[n][ngram] == 1:
                n1 += 1
            if dicts[n][ngram] == 2:
                n2 += 1
    d_c = n1/(n1+2*n2)

print('d_c =', d_c)


def gamma(n, h):
    """ Gamma(history) is the sum of dc/C(h) for every word following that history
        used in the backoff smoothing.
    """
    return len(preds[n].get(h, 0))*d_c/hists[n].get(h, 0)


def backoff_prob(n, hw):
    """Return P(w|h) with a backoff smoothing.
    """
    def pr_back():
        if n == 1:
            return 1/len(lexicon)
        return backoff_prob(n-1, hw[1:])

    h = hw[:-1]
    w = hw[-1]
    if dicts[n].get(hw, 0) > 0:
        return (dicts[n][hw]-d_c)/hists[n][h] + gamma(n, h)*pr_back()
    elif hists[n].get(h, 0) > 0:
        return gamma(n, h)*pr_back()
    else:
        return pr_back()


def verify(prob_fct, n, timer=None):
    """Verifying ∀h sum P(w|h) = 1
    """
    total = len(hists[n])
    for i, hist in enumerate(hists[n]):  # for each history, check that the sums are almost 1
        sum = 0
        for w in lexicon:
            sum += prob_fct(n, hist+(w,))
        if abs(sum - 1) > 1e-5:
            raise Exception('bad probabilities for n=%d: %f' % (n, sum))
        if timer is not None:
            timer.progress(100*i//total)


@static_var(prob=backoff_prob)
def pred(n, h, N=100):
    """Predicts the N most likely next tokens with given history h, using NGrams of order n (could be derived from
    len(h))
    """
    ret = []
    for next in lexicon:
        pr = pred.prob(n, h+(next,))
        ret.append((next, pr))
    ret.sort(key=lambda x: x[1], reverse=True)
    return ret[:N]


# Play the Shannon Game
if __name__ == '__main__':
    hist = []
    for t in ['this', 'be', 'a', 'municipality', 'in', 'the']:
        hist.append(t)
        if len(hist) > 4:
            hist.pop(0)

        for l in range(1, len(hist)+1):
            predictions = pred(l+1, tuple(hist[-l:]))
            print("%s: %s" % (' '.join(hist[-l:]), ' '.join('%s:%0.3f' % r for r in predictions)))
            if hist[-1] == 'the':
                pos, prob = next(((i, p) for i, (a, p) in enumerate(predictions) if a == 'county'), -1)
                print('county: %dth with prob %f' % (pos+1, prob))