# 11c
iterable_a = range(1, 5)
iterable_b = range(3, 10)


if __name__ == '__main__':
    result = set(iterable_a) - set(iterable_b)
    print(f'{result=}')  # result={1, 2}
