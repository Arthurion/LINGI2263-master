import collections
import pickle

from parsers import *
from shortcuts import *

collector = collections.defaultdict(lambda: [])

skipped_tokens = [
    ',', ';', '!', '?',  # predictable by </s>
    '(', ')', '[', ']', '{', '}',  # TODO context swapping
]
skipped_tokens_parser = p_or(*[p_str(t) for t in skipped_tokens])

special_tokens = [
    '<s>', '</s>', ':', '.',
    "'s", "'ll"
    '\'', '"',  # TODO may handle cited text
    '&', '%', '$',
    '\\', '/', '-', '+', '*',
]
special_tokens_parser = p_or(*[p_str(t) for t in special_tokens])
months = [
    'january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november',
    'december', 'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec'
]

months_parser = p_or(*[p_regex(t, re.IGNORECASE) for t in months])

dates_parser = p_or(
    # p_and(p_regex(r'[0-9 \-,]+'), months_parser, p_regex(r'[0-9 \-,]+')).print("%s"),
    p_phrase(months_parser, p_regex(r'[0-9]+([ ]*\,[ ]*[0-9]+)?'), wp=p_regex(r'[ ]*')),
    p_phrase(p_regex(r'[0-9]+[\-]?'), months_parser, p_opt(p_regex(r'[0-9]+'))),
    p_regex(r'[0-9]{4}(\-[0-9]{1,2}){1,2}'),
)

centuries_parser = p_regex(r'([0-9]+[ ]*th([- ]century)|[^ ]+century)')

special = collections.OrderedDict([ # TODO: Group certain types and make stats on it
    ('<saint>', p_regex(r's(t[ \.]|aint )', re.IGNORECASE)),
    ('<date-range>', p_or(
        p_phrase(p_str('('), dates_parser, p_str('-'), dates_parser, p_str(')')),
        p_phrase(dates_parser, p_str('-'), dates_parser),
    )),
    ('<date>', dates_parser),
    ('<month>', months_parser),
    ('<century>', centuries_parser),
    ('<ith>', p_regex(r'[0-9]+[ ]*(th|st)(?![a-zA-Z0-9])')),
    ('<id>', p_regex(r'#[0-9]+')),
    ('<percentage>', p_regex(r'[0-9]+[ ]*\%')),
    ('<range>', p_regex(r'[0-9]+(\-[0-9]+)+')),
    ('<fraction>', p_regex(r'[0-9]+[ ]*/[ ]*[0-9]+')),
    ('<number>', p_regex(r'[0-9 ]+(\.[0-9]+)?')),
])
to_substitute = p_or(*[special[name].replace(name) for name in special])

# TODO abbrev = p_regex(r'[a-zA-Z]{1,2}\.([a-zA-Z]{1,2}\.?)')
english = p_regex(r'[a-zA-Z0-9]+(-[a-zA-Z0-9]+)*(?!-)')
foreign = p_regex(r'[\w]+([\-][\w]+)*', re.UNICODE).replace('<foreign>')
unknown = p_regex('.*?(?=([a-zA-Z0-9 ]|<\/str>))').replace('<UNK>')

tokenizer = p_mult(
    p_or(to_substitute, english, skipped_tokens_parser, special_tokens_parser, foreign, unknown),
    separator=p_regex(r'[ \n\t]*')
)


def zero_f():
    return 0


class NGrams(object):
    def __init__(self, ns):
        self.nmax = max(ns)
        self.hist = collections.deque()
        self.dicts = {n: collections.defaultdict(zero_f) for n in ns}

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

        if token == '</s>':
            self.hist.clear()

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


@static_var(replacements=[
    (re.compile(r'[ ]'),        ' '),      # no-break space to space
    (re.compile(r'[–−—]'),      '-'),      # dashes
    (re.compile(r'[“”]'),       '"'),      # double-quotes
    (re.compile(r'[‘’]'),       "'"),      # simple quotes
    (re.compile(r'[ ]+\.'),     '.'),     # isolated dots
])
def standardize(str):
    for repl in standardize.replacements:
        str, rep = re.subn(repl[0], repl[1], str)

    return str


if __name__ == '__main__':
    ngrams = NGrams([1, 2, 3, 4, 5])

    with Timer("--- Reading the file and standardizing"):

        f = open('definitions_train.txt', encoding='utf8')
        lines = [standardize(l) for l in f.readlines()]
        f.close()

    with Timer("--- Tokenization") as timer:

        tokens = [None] * len(lines)
        for i, line in enumerate(lines):
            tokens[i] = tokenizer(line)[0]
            timer.progress(100*i//len(lines))

    with Timer("--- Building lexicon"):

        lexicon = collections.defaultdict(zero_f)
        for line in tokens:
            for token in line:
                lexicon[token] += 1

    with Timer("--- Merging names, lowercasing what is possible"):

        to_lower = set()
        names = set()
        for t in lexicon:
            tl = t.lower()
            if tl == t:
                continue
            if lexicon.get(tl, 0) != 0 and lexicon.get(tl, 0)+lexicon[t] >= 3:
                to_lower.add(t)
            # else:
            #     names.add(t)

        for t in to_lower:
            lexicon[t.lower()] += lexicon.pop(t)
        # for t in names:  # TODO: make stats on names, detect cities, ...
        #     lexicon['<name>'] += lexicon.pop(t)  # TODO: handle plurals the same manner

    with Timer("""--- Removing low frequency words """):

        to_delete = {t for t in lexicon if lexicon[t] < 3}
        for t in to_delete:
            lexicon['<UNK>'] += lexicon.pop(t)
        tokens = ((token if lexicon.get(token, None) is not None        # token if in the lexicon
                    else token.lower() if token in to_lower             # lowered token if lowered in the lexicon
                    else '<UNK>' for token in line) for line in tokens) # else <UNK>

    print('%d types in the lexicon (%d deleted)' % (len(lexicon), len(to_delete)))

    with Timer("--- Feeding and interning tokens"):
        intern_dic = {}
        last = None
        for line in tokens:
            for token in line:
                if token == last and token in {'<UNK>','<name>'}:
                    continue
                if token in skipped_tokens:
                    continue

                token = intern(token, intern_dic)
                ngrams.feed(token)
                last = token

    with Timer("--- Pickling the results in lexicon and ngrams files"):
        with open('lexicon', 'wb') as f:
            pickle.dump(lexicon, f)
        with open('ngrams', 'wb') as f:
            pickle.dump(ngrams, f)

    print(ngrams)
    print(len(names))
