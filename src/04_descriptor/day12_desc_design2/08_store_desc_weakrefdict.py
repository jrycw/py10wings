from weakref import WeakKeyDictionary


# 08
class Desc:
    def __init__(self):
        self._data = WeakKeyDictionary()

    def __get__(self, instance, owner_cls):
        if instance is None:
            return self
        return self._data.get(instance)

    def __set__(self, instance, value):
        self._data[instance] = value


class MyClass:
    x = Desc()
    y = Desc()


if __name__ == '__main__':
    my_inst1, my_inst2 = MyClass(), MyClass()

    my_inst1.x = 1
    print(f'{my_inst1.x=}')  # 1

    my_inst2.x = 2
    print(f'{my_inst2.x=}')  # 2
    print(f'{my_inst1.x=}')  # 1

    my_inst1.y = 3
    print(f'{my_inst1.y=}')  # 3

    my_inst2.y = 4
    print(f'{my_inst2.y=}')  # 4
    print(f'{my_inst1.y=}')  # 3

    my_inst1.x = 5
    print(f'{my_inst1.x=}')  # 5
    print(f'{my_inst1.y=}')  # 3

    my_inst2.x = 6
    print(f'{my_inst2.x=}')  # 6
    print(f'{my_inst2.y=}')  # 4
