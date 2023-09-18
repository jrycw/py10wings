# 101
import logging
from types import MethodType


class log:
    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    def __get__(self, instance, owner_class):
        if instance is None:
            return self
        return MethodType(self, instance)


class MyClass:
    @classmethod
    @log
    def class_method(cls):
        pass

    @staticmethod
    @log
    def static_method():
        pass


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    my_inst = MyClass()
    my_inst.class_method()
    my_inst.static_method()
