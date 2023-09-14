# 12b
iterable = range(20)

if __name__ == '__main__':
    wanted = {3, 7, 15}
    result = [item
              for item in iterable
              if item in wanted]
    print(f'{result=}')  # result=[3, 7, 15]
