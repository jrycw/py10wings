# 05
from postman import postman


def dec(item):
    def wrapper(cls):
        name = 'func'
        if obj := getattr(cls, name, None):
            if callable(obj):
                setattr(cls, name, postman(item)(obj))
        return cls
    return wrapper


class Class:
    def func(self):
        ...


if __name__ == '__main__':
    inst = Class()
    dec('xmas_card')(Class)  # Class is mutated
    inst.func()  # item='xmas_card' is received
