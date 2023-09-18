# 02
from types import MethodType


class dec:
    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    def __get__(self, instance, owner_class):
        if instance is None:
            return self
        return MethodType(self, instance)


class MyClass:
    @dec
    def my_func(self, *args, **kwargs):
        pass


if __name__ == '__main__':
    my_inst = MyClass()
    my_inst.my_func()  # ok
