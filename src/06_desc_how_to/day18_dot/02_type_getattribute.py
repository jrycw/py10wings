# 02 Experiment code, not verified
def find_name_in_mro(cls, name, default):
    cls_mro = object.__getattribute__(cls, '__mro__')
    for base in cls_mro:
        base_dict = object.__getattribute__(base, '__dict__')
        if name in base_dict:
            return base_dict[name]
    return default


def type_getattribute(obj, name):
    null = object()
    objtype = type(obj)
    cls_var = find_name_in_mro(objtype, name, null)
    descr_get = getattr(type(cls_var), '__get__', null)
    if descr_get is not null:
        if (hasattr(type(cls_var), '__set__')
                or hasattr(type(cls_var), '__delete__')):
            return descr_get(cls_var, obj, objtype)  # data descriptor
    # ----- modification starts -----
    _cls_var = find_name_in_mro(obj, name, null)
    if _cls_var is not null:
        if getattr(type(_cls_var), '__get__', null) is not null:
            return _cls_var.__get__(None, obj)  # descriptor(of any kind)
        return _cls_var  # class variable
    # ----- modification ends -----
    if descr_get is not null:
        return descr_get(cls_var, obj, objtype)  # non-data descriptor
    if cls_var is not null:
        return cls_var  # metaclass class variable
    raise AttributeError(name)


class MyType(type):
    def __getattribute__(self, name):
        # confirm only call once for each dot access
        print(f'MyType.__getattribute__ is called for {name=}')
        return type_getattribute(self, name)


class NonDataDescriptor:
    def __get__(self, instance, owner_cls):
        return 10


class DataDescriptor:
    def __get__(self, instance, owner_cls):
        return 20

    def __set__(self, instance, value):
        ...


class MyType1(MyType):
    z = DataDescriptor()


class MyType2(MyType1):
    y = NonDataDescriptor()


class MyType3(MyType2):
    x = 1


class DummyClass:
    d = 'dummy'


class MyClass(DummyClass, metaclass=MyType3):
    a = 100
    b = NonDataDescriptor()
    c = DataDescriptor()
    t = 't'


if __name__ == '__main__':
    print(f'{MyClass.x=}')  # 1
    print(f'{MyClass.y=}')  # 10
    print(f'{MyClass.z=}')  # 20
    print(f'{MyClass.a=}')  # 100
    print(f'{MyClass.b=}')  # 10
    print(f'{MyClass.c=}')  # 20
    print(f'{MyClass.d=}')  # 'dummy'
