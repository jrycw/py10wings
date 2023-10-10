# 04
from postman import postman


def dec(item):
    def wrapper(cls):
        name = 'func'
        if obj := vars(cls).get(name):
            if callable(obj):
                setattr(cls, name, postman(item)(obj))
        return cls
    return wrapper


class Class:
    def func(self):
        ...


if __name__ == '__main__':
    inst = Class()

    dec('xmas_card')(Class)
    # Class is mutated.
    # Equivalent to
    # 1.  Class = dec('xmas_card')(Class)
    # 2.
    #     @dec('xmas_card')
    #     class Class:
    #         def func(self):
    #             ...
    inst2 = Class()
    inst2.func()  # item='xmas_card' is received
    inst.func()   # item='xmas_card' is received
