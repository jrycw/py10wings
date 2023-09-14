# 08b
from collections import Counter

iterable = 'a'*1 + 'b'*2 + 'c'*3 + 'd'*4
cnter = Counter(iterable)
# cnter.most_common(1)  # [('d', 4)]

if __name__ == '__main__':
    # list unpacking
    [(d, four)] = cnter.most_common(1)
    print(f'{d=}, {four=}')  # d='d', four=4
