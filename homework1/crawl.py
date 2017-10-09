#! /usr/local/bin/python3

import sys
from digest import extract, format
from stats import Timeout

if __name__ == '__main__':
    timeout = 0
    skipped = 0
    for path in sys.stdin.readlines():
        path = path.strip()
        print('processing', path)

        infile = open(path)
        outfile = open('results/'+path, 'w')

        instr = ''.join(infile.readlines())

        extr = []
        try:
            with Timeout(4):
                extr = extract(instr)
                if not extr:
                    skipped += 1
        except TimeoutError:
            timeout += 1
            print('timeout')
        outfile.write(format(extr))

        infile.close()
        outfile.close()

    print(skipped, "file skipped,", timeout, 'timeouts')