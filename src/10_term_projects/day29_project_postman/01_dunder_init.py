# 01
from postman import postman


class Class:
    def __init__(self, item):
        print(type(self.func))  # method
        self.func = postman(item)(self.func)
        print(type(self.func))  # function

    def func(self):
        ...


if __name__ == '__main__':
    inst = Class('xmas_card')
    inst.func()   # item='xmas_card' is received
    print(vars(inst))  # {'func': <function Class.func at 0x0000023BF70C6840>}
    del vars(inst)['func']
    inst.func()  # nothing shown on the screen
