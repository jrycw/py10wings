# 03b
from collections import UserDict


class MyDict(UserDict):
    def __init__(self, dict_data={}):
        super().__init__()
        self.update(dict_data)
