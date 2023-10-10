# 11
from postman import postman


def send_item(cls, item):
    name = 'func'
    if obj := getattr(cls, name, None):
        if callable(obj):
            setattr(cls, name, postman(item)(obj))
    return cls


class Class:
    def func(self):
        ...


if __name__ == '__main__':
    send_item(Class, 'xmas_card')
    inst = Class()
    inst.func()   # item='xmas_card' is received
