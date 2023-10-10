# 10a
from postman import postman


def send_item(cls, item):
    name = 'func'
    if obj := vars(cls).get(name):
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
    inst.func()   # nothing shown on the screen
