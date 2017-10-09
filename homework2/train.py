import collections
import pickle
import copy
from fractions import Fraction

from parsers import *
from shortcuts import *

# Some special characters to be replaced
special_chars = [
    (re.compile(r'[ ]'),            ' '),       # no-break space to space
    (re.compile(r'[–−—]'),          '-'),       # dashes
    (re.compile(r'[“”]'),           '"'),       # double-quotes
    (re.compile(r'[‘’]'),           "'"),       # simple quotes
    (re.compile(r'[\{\[]'),         '('),       # left parenthesis
    (re.compile(r'[\}\]]'),         ')'),       # right parenthesis

    (re.compile(r',([ ]*,)+'),         ','),    # correct ', ,'
    (re.compile(r' ?\.\.[ ]*\.]'),   ' ...'),   # correct 'dr.. .'
]


def remove_special_chars(str):
    for repl in special_chars:
        str, rep = re.subn(repl[0], repl[1], str)

    return str

# Grouping to be made with months, dates without spaces into it, percentages, ...
groupings = [
    ('<month>', re.compile(r'^(January|February|March|April|May|June|July|August|September|October|November|December)$')),
    ('<date>', re.compile(r'^[0-9]{4}(\-[0-9]{1,2}){1,2}$')),
    ('<range>', re.compile(r'^[0-9]+\-[0-9]+$')),
    ('<percentage>', re.compile(r'^[0-9]+(\.[0-9]+)?%$')),
    ('<ith>', re.compile(r'^[0-9]+(th|st)$')),
    ('<number>', re.compile(r'^[0-9]+(\.[0-9]+)?$')),
    ('<quantity>', re.compile(r'^[0-9]+(\.[0-9]+)?')),
]
abbrev = re.compile('^([a-zA-Z]{1,2}(\.[a-zA-Z]{1,2})?|[A-Z][a-z]{1,2})$')

english = re.compile(r'^[a-zA-Z0-9]+(-[a-zA-Z0-9]+)*$')
foreign = re.compile(r'^[\w]+(-[\w]+)*$', re.UNICODE)
# is foreign if foreign matches but not english
is_foreign = lambda token: english.match(token) is None and foreign.match(token) is not None


def reformat_line(line):
    """Reformats a line, splitting "'s", adding <s> and </s> tokens after ending dots... And also detects foreign words
    """
    ret = []
    skip_until = -1
    for i, token in enumerate(line):
        # For each token in the line
        # Have we processed
        if i < skip_until:
            continue

        # Look if the end of a sentence
        if token == '.' and (len(line) > i+1 and line[i+1] != '</s>') and abbrev.match(line[i-1]) is None:
            ret.extend(['.', '</s>', '<s>'])
            continue

        # If parenthesis and extract = true
        if token == '(':
            closing = next((i+j+1 for j, token in enumerate(line[i+1:]) if token == ')'), -1)
            # Malformed parenthesis => cut
            if closing == -1:
                ret.extend(['.', '</s>'])
                break

        # Look if we want to group the token
        repl = next((substit for substit, reg in groupings if reg.match(token) is not None), None)
        if repl:
            ret.append(repl)
            continue

        # If is foreign
        if is_foreign(token):
            ret.append('<foreign>')
            continue

        # token's => token 's
        if token.endswith("'s") and len(token) > 2:
            ret.append(token[:-2])
            ret.append("'s")
            continue

        # tokens' => tokens 's
        if token.endswith("s'") and len(token) > 2:
            ret.append(token[:-1])
            ret.append("'s")
            continue

        # Otherwise, just
        ret.append(token)

    return ret


def tokenizer(line):
    """Called to get the tokens from a line"""
    return (reformat_line(remove_special_chars(line).split())), len(line)

# Now, some hardcoded rules for lemmatization
hardcoded_rules = {
    'be': ['be', 'is', 'are', 'am', 'was', 'were', 'been', 'being'],
    'have': ['have', 'has', 'had', 'having'],
    'race': ['race', 'racing'],
    'lie': ['lie', 'lying'],
    'lay': ['lay', 'laid'],
    'get': ['get', 'getting', 'got'],
    'lead': ['lead', 'led'],
    'ring': ['ring', 'rang', 'rung'],
    'drink': ['drink', 'drank', 'drunk'],

    # some plurals
    'gas': ['gas', 'gases'],
    'toe': ['toe', 'toes'],

    # not to be matched ending by s
    'us': ['us'],
    'as': ['as'],
    'this': ['this'],
}
def _(dic):
    ret = {}
    for std, lst in dic.items():
        for l in lst:
            ret[l] = std
    return ret
hardcoded_rules = _(hardcoded_rules)

# Some more generic rules for lemmatization
simplify_rules = [
    (r'y',                  re.compile(r'ies$')),  # berries
    (r'o',                  re.compile(r'oes$')),  # tomatoes, mosquitoes, goes, does, ...
    (r'\1',                 re.compile(r'([a-z][^s])s$')),  # gaps, not pass
    (r'y',                  re.compile(r'(?=[a-z]{2})ied$')),  # fried, dried, ...
    (r'',                   re.compile(r'(?=[a-z]{2})ed$')),  # detected
    (r'\1',                 re.compile(r'(?<=([a-z]))\1ing$')),  # spinning, hitting, ...
    (r'',                   re.compile(r'(?<=[a-z]{2})ing$')),  #  wearing, ... but not wing
    (r'e',                  re.compile(r'(?<=(t|d))\1en$')),  # written, hidden, ...
    (r'',                   re.compile(r'en$')),  # beaten, eaten, ...
]


def simplify(token):
    """Get the lemma for a token, returns None if no"""
    if not token[0].islower():
        return None
    canon = hardcoded_rules.get(token, None)
    if canon is not None:
        return canon
    canons = (re.sub(plur, sin, token) for sin, plur in simplify_rules)
    while True:
        canon = next(canons, None)
        if canon is None:
            return None
        if canon != token:
            return canon


def zero_f():
    """simply lambda: 0 for NGrams to be picklable"""
    return 0


class NGrams(object):
    def __init__(self, ns):
        self.nmax = max(ns)
        self.hist = collections.deque()
        self.hist_stack = []
        self.dicts = {n: collections.defaultdict(zero_f) for n in ns}

    def push(self):
        self.hist_stack.append(copy.copy(self.hist))

    def pop(self):
        self.hist = self.hist_stack.pop()

    def is_in_subcontext(self):
        return len(self.hist_stack) > 0

    def clear(self):
        self.hist.clear()

    def feed(self, token):
        self.hist.append(token)
        if len(self.hist) > self.nmax:
            self.hist.popleft()
        hist = tuple(self.hist)

        # feeding the history into dictionaries
        for n in self.dicts:
            dict = self.dicts[n]
            if len(hist) >= n:
                dict[hist[-n:]] += 1

    def __str__(self):
        s = []
        for n in self.dicts:
            dict = self.dicts[n]
            s.append("\n=== %d-grams===" % (n,))
            list = [(k, dict[k]) for k in dict]
            list = sorted(list, key=lambda t: t[1], reverse=True)
            for v in list[:20]:
                s.append(' '.join(v[0])+": "+str(v[1]))
            s.append("===/%d-grams===" % (n,))

        return '\n'.join(s)

only_commas = re.compile('^<s>[  ,]*</s>[  ]?$')

if __name__ == '__main__':
    ngrams = NGrams([1, 2, 3, 4, 5])

    with Timer("--- Reading the file"):

        f = open('definitions_train.txt', encoding='utf8')
        lines = [l for l in f.readlines() if only_commas.match(l) is None]
        f.close()

    with Timer("--- Checking strings and Tokenizing") as timer:

        tokens = [None] * len(lines)
        for i, line in enumerate(lines):
            tokens[i] = tokenizer(line)[0]
            timer.progress(100*i//len(lines))

        # Same but without feedback:
        # tokens = [tokenizer(line)[0] for line in lines]

    # Uncomment to see the transformed text
    # print('\n'.join([' '.join(token for token in line) for line in tokens]))
    # exit(0)

    with Timer("--- Building lexicon"):

        lexicon = collections.defaultdict(zero_f)
        for line in tokens:
            for token in line:
                lexicon[token] += 1

    print(len(lexicon), 'distinct types after tokenization')

    with Timer("--- Merging names, lowercasing what is possible"):

        to_lower = {}
        for T in lexicon:
            t = T.lower()
            if T == t:
                continue
            if lexicon.get(t, 0) != 0 and lexicon[T]+lexicon[t] >= 3:
                to_lower[T] = t

        for T, t in to_lower.items():
            lexicon[t] += lexicon.pop(T)

        tokens = [[to_lower.get(token, token) for token in line] for line in tokens]

    print(len(lexicon), 'distinct types after lowercasing')

    with Timer("--- Merging plurals and verb forms, ..."):

        to_simplify = {}

        for ts in lexicon:
            t = simplify(ts)
            if t is not None and lexicon.get(t, 0) != 0 and lexicon[t]+lexicon[ts] >= 3:
                to_simplify[ts] = t

        for ts, t in to_simplify.items():
            lexicon[t] += lexicon.pop(ts)

        tokens = [[to_simplify.get(token, token) for token in line] for line in tokens]

    print(len(lexicon), 'distinct types after lemmatization')

    with Timer("--- Removing low frequency words "):

        to_delete = {t for t in lexicon if lexicon[t] < 3}
        for t in to_delete:
            lexicon['<UNK>'] += lexicon.pop(t)
        tokens = [[token if lexicon.get(token, None) is not None        # token if in the lexicon
                   else '<UNK>' for token in line] for line in tokens]  # else <UNK>

    print(len(lexicon), 'distinct types after removal of the least frequents')
    print('%d types in the lexicon (%d deleted)' % (len(lexicon), len(to_delete)))

    types = [(k, lexicon[k]) for k in lexicon]
    types.sort(key=lambda x:x[1], reverse=True)
    for i, t in enumerate(types[:20]):
        print("%d & %s & %d \\\\ \hline" % (i+1, t[0], t[1]))

    # Uncomment not to compute NGrams
    # exit(0)

    with Timer("--- Feeding and interning tokens"):
        intern_dic = {}
        for line in tokens:
            for token in line:
                token = intern(token, intern_dic)
                if token in {'('}:
                    ngrams.push()
                    ngrams.clear()
                ngrams.feed(token)
                if token in {')'} and ngrams.is_in_subcontext():
                    ngrams.pop()
                if token in {'</s>'}:
                    ngrams.clear()
    print(ngrams)

    # Uncomment not to export the results
    # exit(0)

    with Timer("--- Pickling the results in lexicon and ngrams files"):
        with open('lexicon', 'wb') as f:
            pickle.dump(lexicon, f)
        with open('ngrams', 'wb') as f:
            pickle.dump(ngrams, f)
