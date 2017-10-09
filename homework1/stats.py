#! /usr/local/bin/python3

import sys
import signal
import collections
import digest


class Timeout:

    def __init__(self, seconds=3):
        self.seconds = seconds

    @staticmethod
    def handle_timeout(signum, frame):
        raise TimeoutError()

    def __enter__(self):
        signal.signal(signal.SIGALRM, Timeout.handle_timeout)
        signal.alarm(self.seconds)

    def __exit__(self, type, value, traceback):
        signal.alarm(0)


if __name__ == '__main__':
    last = collections.defaultdict(lambda: 0)
    full = collections.defaultdict(lambda: 0)

    timeouts = 0
    empty_count = 0
    ok_count = 0
    item_count = 0
    units = 0
    quantities = 0

    for path in sys.stdin.readlines():
        path = path.strip()
        print('processing', path)

        f = open(path)
        ss = ''.join(f.readlines())
        f.close()
        try:
            with Timeout(4):
                items = digest.extract(ss)

            if not items:
                empty_count += 1
            else:
                ok_count += 1

            for item in items:
                item_count += 1
                last[item[3].split(' ')[-1]] += 1
                full[item[3]] += 1
                if item[0]:
                    quantities += 1
                if item[1]:
                    units += 1
        except TimeoutError:
            print('timeout')
            timeouts += 1


    fullcounts = []
    different = 0
    once = 0
    for k in full:
        fullcounts.append((full[k], k))
        if full[k] == 1:
            once += 1
        different += 1
    fullcounts.sort(reverse=True)
    # print(fullcounts)

    print(different, "distinct ingredient,", once, 'appear only once')

    different = 0
    once = 0

    lastcounts = []
    for k in last:
        lastcounts.append((last[k], k))
        if last[k] == 1:
            once += 1
        different += 1
    lastcounts.sort(reverse=True)
    # print(lastcounts)

    print(different, "distinct last-word ingredient,", once, 'appear only once')

    for i in range(0, min(25, len(lastcounts))):
        print(i+1, "&", fullcounts[i][1], "&", fullcounts[i][0], "&", lastcounts[i][1], "&", lastcounts[i][0],
              "\\\\ \\hline")

    print(ok_count, 'files scanned,', empty_count, 'skipped,', timeouts, 'timeouts')
    print(item_count, 'ingredients found,', quantities, 'quantities and', units, 'units')