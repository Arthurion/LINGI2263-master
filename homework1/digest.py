#! /usr/local/bin/python3

import sys

from bs4 import BeautifulSoup
import yaml

# custom libraries are commented as well!
# our hand-crafted parser combinators library
from parsers import *
# our hand-crafted dictionaries
import dictionaries


# We don't want a letter after the undesirable word
undesirable = p_or(*[p_regex(reg+'(?![a-z])') for reg in dictionaries.undesirables])

# A unit isn't glued to another letter
unit = p_or(*[p_regex(reg+'(?![a-z])') for reg in dictionaries.units])

# An ingredient can be many words(we accept "(14oz.)" for instance), but then isn't glued to any letter
ingredient = p_or(*[p_regex('([a-z0-9\(\)\-\.\%]* )*?'+reg+'(?![a-z\-])') for reg in dictionaries.ingredients])

# A quantity is a number, a fraction, a range, 'some', ...
quantity = p_regex(r'([0-9\+\-\/¼½¾⅓⅔⅕⅖⅗⅘⅙⅚⅛⅜⅝⅞ ]|to(?![a-z])|some(?![a-z]))+')

# A commentary is just the end of the sentence, usually
commentary = p_regex(r'.*')


# item is a parser for what should describe an item in a ingredients list
item = p_phrase(
    p_opt(quantity, ''),
    p_opt(unit, ''),
    p_opt(p_str('of'), ''),
    ingredient,
    p_opt(commentary, '')
)

_white = re.compile(r'^[\n\t ]*$')


def format(l):
    """ Formats a given list of items to the YAML format """
    ret = []
    for i in l:
        d = dict()
        d['ingredient'] = i[3]
        if i[1]:
            d['unit'] = i[1]
        if i[0]:
            d['quantity'] = i[0].strip()
        ret.append(d)
    return yaml.dump(ret, allow_unicode=True)


def extract(instr, debug=False):
    """
        Extracts ingredients in a HTML document presenting a receipt. The ingredients must be listed in li tags! and be
        formatted in a quantity unit ('of') ingredient
    """
    d = BeautifulSoup(instr, 'lxml')
    items = []

    for li in d.find_all('li'):
        if len(li.find_all('a')) > 0:
            # We don't want links in our items (otherwise, could be links across the website)
            continue

        text = li.get_text()
        # is it only white spaces?
        if _white.match(text):
            continue

        txt = text.lower()

        txt = txt.replace('\n', '')
        # look for an undesirable expression at the beginning of the phrase. If one, skip!
        _, l = undesirable(txt, 0)
        if l >= 0:
            continue
        # else, try to parse the item and if success, add it to ingredients
        a, l = item(txt, 0)
        if debug:
            print(text)
        if l >= 0:
            if debug:
                print(a)
            items.append(a)

    return items


if __name__ == '__main__':
    argc = len(sys.argv)

    infile = sys.stdin
    outfile = sys.stdout

    if argc > 1:
        infile = open(sys.argv[1])
    if argc > 2:
        outfile = open(sys.argv[2], 'w')

    instr = ''.join(infile.readlines())
    outfile.write(format(extract(instr)))

    infile.close()
    outfile.close()
