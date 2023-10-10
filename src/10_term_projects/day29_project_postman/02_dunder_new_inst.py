# 02
from postman import postman


class Class:
    def __new__(cls, item):
        inst = super().__new__(cls)
        inst.func = postman(item)(inst.func)
        return inst

    def func(self):
        ...


if __name__ == '__main__':
    inst = Class('xmas_card')
    inst.func()   # item='xmas_card' is received
