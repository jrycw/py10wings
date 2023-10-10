# 11a
from postman import postman


def send_item(cls, item):
    name = 'func'
    if obj := getattr(cls, name, None):
        if callable(obj):
            setattr(cls, name, postman(item)(obj))
    return cls


item = 'xmas_card'


class ParentClass:
    def func(self):
        ...


class Class(ParentClass):
    ...


if __name__ == '__main__':
    send_item(Class, 'xmas_card')
    inst = Class()
    inst.func()   # item='xmas_card' is received
