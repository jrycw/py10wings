# 12
from postman import postman


class Class:
    item = 'xmas_card'

    @postman(item)
    def func(self):
        ...


if __name__ == '__main__':
    inst = Class()
    inst.func()  # item='xmas_card' reveived
