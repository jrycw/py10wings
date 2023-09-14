# 08c
from collections import Counter

iterable = 'a'*1 + 'b'*2 + 'c'*3 + 'd'*4
cnter = Counter(iterable)
# cnter.most_common(1)  # [('d', 4)]

if __name__ == '__main__':
    # `*` can be used in list unpacking as well
    [(a, *_)] = [('a', 'b', 'c')]
    print(f'{a=}, {_=}')  # a='a', _=['b', 'c']
