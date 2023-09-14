# 03c
from collections import UserDict


class MyDict(UserDict):
    def __init__(self, dict_data={}):
        super().__init__()
        self._dict_data = dict_data
        self.update(dict_data)


if __name__ == '__main__':
    d, d2 = MyDict(), MyDict()
    print(d._dict_data is d2._dict_data)  # True
    print(d, d2)  # {}, {}
    d._dict_data['a'] = 1
    print(d._dict_data is d2._dict_data)  # True
    print(d._dict_data, d2._dict_data)  # {'a': 1} {'a': 1}
