# 09b
from itertools import count
from string import ascii_lowercase

if __name__ == '__main__':
    # [str, int]
    d = dict(zip(ascii_lowercase, count(1)))
    keys, values = zip(*d.items())
