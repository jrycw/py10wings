# 03
from postman import postman


class Class:
    def __new__(cls, item):
        cls.func = postman(item)(cls.func)
        inst = super().__new__(cls)
        return inst

    def func(self):
        ...


if __name__ == '__main__':
    Class('xmas_card'), Class('mail')
    inst = Class('package')
    inst.func()
    # item='package' is received
    # item='mail' is received
    # item='xmas_card' is received
