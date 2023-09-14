# 11a
iterable_a = range(1, 5)
iterable_b = range(3, 10)

if __name__ == '__main__':
    result = [a
              for a in iterable_a
              if a not in iterable_b]
    print(f'{result=}')  # result=[1, 2]
