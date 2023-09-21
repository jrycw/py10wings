# 01c
class myprop:
    def __init__(self, doc=None):
        self.__doc__ = doc

    def __get__(self, instance, owner_cls):
        if instance is None:
            return self
        return getattr(instance, self._name)

    def __set__(self, instance, value):
        name = self._name[1:]
        cls_name = type(instance).__name__
        raise AttributeError(
            f"myprop '{name}' of '{cls_name}' object has no setter")

    def __delete__(self, instance):
        name = self._name[1:]
        cls_name = type(instance).__name__
        raise AttributeError(
            f"myprop '{name}' of '{cls_name}' object has no deleter")

    def __set_name__(self, owner_cls, name):
        self._name = f'_{name}'


class MyClass:
    x = myprop()
    y = myprop()
    z = myprop()

    def __init__(self, x, y, z):
        self._x = x
        self._y = y
        self._z = z


if __name__ == '__main__':
    my_inst = MyClass(1, 1, 1)
    print(my_inst.x)  # 1
    print(my_inst.y)  # 1
    print(my_inst.z)  # 1

    # my_inst.x = 2  # ValueError
    # my_inst.y = 2  # ValueError
    # my_inst.z = 2  # ValueError

    print(f'{MyClass.x.__doc__=}')
    print(f'{MyClass.y.__doc__=}')
    print(help(MyClass.x))
