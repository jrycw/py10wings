# 04
class TargetClass:
    def __init__(self, **kwargs):
        """
        kwargs: {'x': 1, 'y':2, ...}
        """
        self.__dict__.update({f'_{k}': v for k, v in kwargs.items()})

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    ...


class MyType1(type):
    """WRONG impl:
    property(lambda self: getattr(self, f'_{prop}'
    """
    def __new__(mcls, cls_name, cls_bases, cls_dict, **kwargs):
        cls = super().__new__(mcls, cls_name, cls_bases, cls_dict)

        def init(self, **kwargs):
            self.__dict__.update({f'_{k}': v for k, v in kwargs.items()})
        cls.__init__ = init
        for prop in kwargs:
            setattr(cls,
                    prop,
                    property(lambda self: getattr(self, f'_{prop}')))
        return cls


class MyType2(type):
    """Better impl:
    property(lambda self, attr=prop: getattr(self, f'_{attr}'))
    """
    def __new__(mcls, cls_name, cls_bases, cls_dict, **kwargs):
        cls = super().__new__(mcls, cls_name, cls_bases, cls_dict)

        def init(self, **kwargs):
            self.__dict__.update({f'_{k}': v for k, v in kwargs.items()})
        cls.__init__ = init
        for prop in kwargs:
            setattr(cls,
                    prop,
                    property(lambda self, attr=prop: getattr(self, f'_{attr}')))
        return cls


kwds = {'x': 1, 'y': 2}


class MyClass1(metaclass=MyType1, **kwds):
    pass


class MyClass2(metaclass=MyType2, **kwds):
    pass


if __name__ == '__main__':
    my_inst1 = MyClass1(**kwds)
    print(vars(my_inst1))  # {'_x': 1, '_y': 2}
    print(my_inst1.x, my_inst1.y)  # 2 2 <= incorrect

    my_inst2 = MyClass2(**kwds)
    print(vars(my_inst2))  # {'_x': 1, '_y': 2}
    print(my_inst2.x, my_inst2.y)  # 1 2
