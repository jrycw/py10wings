# 01b
class myprop:
    def __get__(self, instance, owner_cls):
        if instance is None:
            return self
        return getattr(instance, self._name)

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
    print(my_inst.x)  # 1 from __get__
    my_inst.x = 2
    print(my_inst.__dict__)  # {'_x': 1, '_y': 1, '_z': 1, 'x': 2}
    print(my_inst.x)  # 2 from my_inst.__dict__
