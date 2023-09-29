# 03 Experiment code, not verified
def find_name_in_mro(cls, name, default):
    "Emulate _PyType_Lookup() in Objects/typeobject.c"
    for base in cls.__mro__:
        if name in vars(base):
            return vars(base)[name]
    return default


def object_setattr(obj, name, value):
    null = object()
    objtype = type(obj)
    cls_var = find_name_in_mro(objtype, name, null)
    descr_get = getattr(type(cls_var), '__get__', null)
    descr_set = getattr(type(cls_var), '__set__', null)
    if descr_get is not null and descr_set is not null:
        descr_set(cls_var, obj, value)  # data descriptor
        return
    if hasattr(obj, '__dict__'):
        obj.__dict__[name] = value  # instance variable
        return
    raise AttributeError(name)


class DataDescriptor:
    def __get__(self, instance, owner_cls):
        print('__get__ called')
        if instance is None:
            return self
        return instance.__dict__.get(self._name)

    def __set__(self, instance, value):
        print('__set__ called')
        instance.__dict__[self._name] = value

    def __set_name__(self, owner_cls, name):
        self._name = name


class Character:
    dog = DataDescriptor()

    def __init__(self, name):
        self.name = name

    def __setattr__(self, name, value):
        print(f'Character.__setattr__ is called for {name=}. {value=}')
        object_setattr(self, name, value)


if __name__ == '__main__':
    john_wick = Character('John Wick')
    print(john_wick.name)  # John Wick
    john_wick.dog = 'Daisy'  # __set__ called
    print(john_wick.dog)  # __get__ called, Daisy
    print(john_wick.__dict__)  # {'name': 'John Wick' 'dog': 'Daisy'}
