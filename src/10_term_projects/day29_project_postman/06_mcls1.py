# 06
from postman import postman


class Meta(type):
    def __new__(mcls, cls_name, cls_bases, cls_dict, item):
        cls = super().__new__(mcls, cls_name, cls_bases, cls_dict)
        name = 'func'
        if obj := vars(cls).get(name):
            if callable(obj):
                setattr(cls, name, postman(item)(obj))
        return cls


item = 'xmas_card'


class Class(metaclass=Meta, item=item):
    def func(self):
        ...


if __name__ == '__main__':
    inst = Class()
    inst.func()  # item='xmas_card' is received
