# 12a
iterable = range(20)

if __name__ == '__main__':
    result = [item
              for item in iterable
              if item == 3 or item == 7 or item == 15]
    print(f'{result=}')  # result=[3, 7, 15]
