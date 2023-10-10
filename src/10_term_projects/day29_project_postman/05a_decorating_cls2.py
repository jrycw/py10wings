# 05a
from postman import postman


def dec(item):
    def wrapper(cls):
        name = 'func'
        if obj := getattr(cls, name, None):
            if callable(obj):
                setattr(cls, name, postman(item)(obj))
        return cls
    return wrapper


class ParentClass:
    def func(self):
        ...


class Class(ParentClass):
    pass


if __name__ == '__main__':
    inst = Class()
    dec('xmas_card')(Class)
    inst.func()  # item='xmas_card' is received
