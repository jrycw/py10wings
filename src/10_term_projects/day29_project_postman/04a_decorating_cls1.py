# 04a
from postman import postman


def dec(item):
    def wrapper(cls):
        name = 'func'
        if obj := vars(cls).get(name):
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
    inst.func()   # nothing shown on the screen
