README
======

All the files are written in Python 3, so please don't loose time trying to run
it on Python 2. Also, switching from the training set and the testing one has to
be done by hand in the code. We usually load the file at the very beginning of
every script.

We tried to make our scripts give you some feedbacks about the computation
progression. We hoped it would a bit more pleasant for you to wait.

THIS IS THE FIRST SCRIPT TO RUN:
The train.py file will produce the lexicon and the ngrams from the training set.
They will be stored in two files, used the Pickle python module. (in the
standard library)

The estimation.py file will play the Shannon game, but will also be used by
others because it builds the prediction trees at runtime from the ngrams file.

The consistency.py file tries on hardcoded and random histories from the test
set and checks the sum of the probabilities for all possible predictions given
an history is 1. We used to use fractions to have exact results, and it all
worked fine, but was really slow, so now we just take 10^-8 as error margin.

The perplexity.py file computes the perplexity our model encounters while trying
to predict the testing set. It also prints the OOV.

The stats.py file plots the n-grams histogram using a stem plot, but requires
matplotlib in order to work.

We hope you will have a much fun as we did!
