# 05
class MyType(type):
    @classmethod
    def __prepare__(cls, cls_name, cls_bases, **kwargs):
        print('MyType __prepare__ called')
        cls_dict = {}
        print(f'{id(cls_dict)=}')
        return cls_dict

    def __new__(mcls, cls_name, cls_bases, cls_dict):
        print('MyType __new__ called')
        print(f'{id(cls_dict)=}')
        cls = super().__new__(mcls, cls_name, cls_bases, cls_dict)
        return cls


class MyClass(metaclass=MyType):
    pass
