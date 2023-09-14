# 03d
from collections import UserDict


class MyDict(UserDict):
    def __init__(self, dict_data=()):
        print(f'{id(dict_data)=}')
        super().__init__()
        self._dict_data = dict_data
        self.update(dict_data)


if __name__ == '__main__':
    d, d2 = MyDict(), MyDict()
    print(d._dict_data is d2._dict_data)  # True
    print(d, d2)  # {}, {}
    d._dict_data = (1,)
    print(d._dict_data is d2._dict_data)  # False
    print(d._dict_data, d2._dict_data)  # (1,) ()
