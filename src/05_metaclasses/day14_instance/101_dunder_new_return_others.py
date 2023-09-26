# 101
from types import SimpleNamespace


class MyClass:
    def __new__(cls, x):
        return SimpleNamespace()

    def __init__(self, x):
        self.x = x

    def hi(self):
        return 'hi'


if __name__ == '__main__':
    my_inst = MyClass(1)  # __init__ not being called
    print(type(my_inst))  # <class 'types.SimpleNamespace'>
    MyClass.__init__(my_inst, 1)
    print(my_inst.__dict__)  # {'x': 1}
    print(MyClass.hi(my_inst))  # hi
