# C'EST UN BROUILLON :P

import re

n = set()
t = set()
r = {} # the key is the rule, the value is the associated probability
s = 'SBARQ'
# G = (N,E,R,S)

dico_words = {} # a dictionary where keys are words (the, do, like, etc.) and values are a list of symbol for this word.
list_rules = [] # each item of the list is a list representing a rule: [a, b, c] = a -> b c (it seems that there is no rule of the type a -> b in the train.txt).

def separate_strings(str):
    """ Assuming that the string is of the form ( b )( a ) with other parentheses in a and b, we return a tuple: (b,a) """
    i = 0 # position in the string
    nb_parentheses = 0 # the number of opened parentheses encountered.
    for s in str:
        if str[i] == '(':
            nb_parentheses += 1
        elif str[i] == ')':
            nb_parentheses -= 1
        if nb_parentheses == 0:
            break
        i += 1
    return str[:i+1], str[i+1:]

def readParenthese(str):
    str_cleared = str[1:-1] # we delete the first and last parentheses.
    symbol, word = str_cleared.split(" ", maxsplit=1) # we only split the string once.
    print(word)
    if word[0] != '(': # if we have a terminal symbol
        t.add(symbol)
        if word in dico_words and symbol not in dico_words[word]:
            dico_words[word].append(symbol)
        elif word not in dico_words:
            dico_words[word] = [symbol]
        return symbol
    else: # if we have a non-terminal symbol
        n.add(symbol)
        str1, str2 = separate_strings(word) # the word being ( a )( b ), str1 = a and str2 = b
        symbol1 = readParenthese(str1)
        symbol2 = readParenthese(str2)

        if [symbol, symbol1, symbol2] not in list_rules:
            list_rules.append([symbol, symbol1, symbol2])

        return symbol

if __name__ == '__main__':
    f = open('QuestionBank/train.txt', encoding='utf8')
    for line in f.readlines():
        line = line[:-1] # to delete the end space
        readParenthese(line)
    print(dico_words)
