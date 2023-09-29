# 04 Experiment code, not verified
def find_name_in_mro(cls, name, default):
    "Emulate _PyType_Lookup() in Objects/typeobject.c"
    for base in cls.__mro__:
        if name in vars(base):
            return vars(base)[name]
    return default


def type_setattr(obj, name, value):
    """Just exploring the magic of Python, don't do this..."""
    if hasattr(obj, '__dict__'):
        cls_name = obj.__name__
        cls_bases = obj.__mro__
        cls_dict = dict(vars(obj)) | {name: value}
        _globals = globals() | {'cls_name':  cls_name,
                                'cls_bases': cls_bases,
                                'cls_dict': cls_dict}
        meta = type(obj).__name__
        cls_body = f'{cls_name}={meta}(cls_name, cls_bases, cls_dict)'
        exec(cls_body, _globals, globals())
    else:
        raise AttributeError(name)


class MyType(type):
    def __setattr__(self, name, value):
        print(f'MyType.__setattr__ is called for {name=}. {value=}')
        type_setattr(self, name, value)


class DataDescriptor:
    def __get__(self, instance, owner_cls):
        if instance is None:
            return self
        return instance.__dict__.get(self._name)

    def __set__(self, instance, value):
        instance.__dict__[self._name] = value

    def __set_name__(self, owner_cls, name):
        self._name = name


class MyClass(metaclass=MyType):
    a = 'a'


if __name__ == '__main__':
    orig_cls_id = id(MyClass)
    print(MyClass.a)  # a
    MyClass.a = 'b'
    print(MyClass.a)  # b
    assert orig_cls_id != id(MyClass)

    MyClass.c = DataDescriptor()
    my_inst = MyClass()
    my_inst.c = 'c'
    print(my_inst.c)  # c
    print(MyClass.c)  # <__main__.DataDescriptor object at 0x0000014667AE6690>
