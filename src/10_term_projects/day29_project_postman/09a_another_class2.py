# 09a
from postman import postman


class Meta(type):
    def __new__(mcls, cls_name, cls_bases, cls_dict, item):
        cls = super().__new__(mcls, cls_name, cls_bases, cls_dict)
        name = 'func'
        if obj := getattr(cls, name, None):
            if callable(obj):
                setattr(cls, name, postman(item)(obj))
        return cls


def send_item(item):
    def wrapper(cls):
        return Meta(cls.__name__, cls.__bases__, dict(vars(cls)), item=item)
    return wrapper


item = 'xmas_card'


class ParentClass:
    def func(self):
        ...


@send_item(item)
class Class(ParentClass):
    ...


if __name__ == '__main__':
    inst = Class()
    inst.func()  # item='xmas_card' is received
