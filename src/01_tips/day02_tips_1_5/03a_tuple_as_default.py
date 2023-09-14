# 03a
from collections import UserDict


class MyDict(UserDict):
    def __init__(self, dict_data=None):
        super().__init__()
        if dict_data is not None:
            self.update(dict_data)
