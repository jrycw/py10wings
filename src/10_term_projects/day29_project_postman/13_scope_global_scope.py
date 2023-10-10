# 13
from postman import postman

item = 'xmas_card'


class Class:

    @postman(item)
    def func(self):
        ...


if __name__ == '__main__':
    inst = Class()
    inst.func()  # item='xmas_card' reveived
