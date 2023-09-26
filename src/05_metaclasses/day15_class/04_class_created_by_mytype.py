# 04
class MyClass1:
    def __init__(self, x):
        self.x = x


class MyClass2(object):
    def __init__(self, x):
        self.x = x


class MyClass3(object, metaclass=type):
    def __init__(self, x):
        self.x = x


class MyType(type):
    def __new__(mcls, cls_name, cls_bases, cls_dict):
        cls = super().__new__(mcls, cls_name, cls_bases, cls_dict)
        return cls


class MyClass(object, metaclass=MyType):
    def __init__(self, x):
        self.x = x
