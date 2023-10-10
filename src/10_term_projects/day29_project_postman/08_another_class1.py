# 08
from postman import postman


class Meta(type):
    def __new__(mcls, cls_name, cls_bases, cls_dict, item):
        cls = super().__new__(mcls, cls_name, cls_bases, cls_dict)
        name = 'func'
        if obj := vars(cls).get(name):
            if callable(obj):
                setattr(cls, name, postman(item)(obj))
        return cls


def send_item(item):
    def wrapper(cls):
        return Meta(cls.__name__, cls.__bases__, dict(vars(cls)), item=item)
    return wrapper


item = 'xmas_card'


@send_item(item)
class Class:
    def func(self):
        ...


if __name__ == '__main__':
    inst = Class()  # type(Class) => <class '__main__.Meta'>
    inst.func()  # item='xmas_card' is received
