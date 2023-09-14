# 09a
from string import ascii_lowercase

if __name__ == '__main__':
    # [str, int]
    d = {k: v
         for k, v in zip(ascii_lowercase, range(1, 27))}
