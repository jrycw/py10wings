# 07
class Desc:
    def __get__(self, instance, owner_cls):
        if instance is None:
            return self
        return instance.__dict__.get(self._name)

    def __set__(self, instance, value):
        instance.__dict__[self._name] = value

    def __set_name__(self, owner_cls, name):
        self._name = name


class MyClass:
    x = Desc()
    y = Desc()


if __name__ == '__main__':
    my_inst = MyClass()
    my_inst.x = 0
    print(f'{my_inst.__dict__=}')  # {'x': 0}
    print(f'{my_inst.x=}')  # 0

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
