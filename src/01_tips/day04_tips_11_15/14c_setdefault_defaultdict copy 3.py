# 14c
from collections import defaultdict

data = [('a', 1), ('b', 2), ('c', 3), ('a', 4)]

if __name__ == '__main__':
    d = defaultdict(list)
    for name, value in data:
        d[name].append(value)
