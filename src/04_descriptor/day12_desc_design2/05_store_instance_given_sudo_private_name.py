# 05
class Desc:
    def __init__(self, name):
        self._name = f'_{name}'

    def __get__(self, instance, owner_cls):
        if instance is None:
            return self
        return getattr(instance, self._name, None)

    def __set__(self, instance, value):
        setattr(instance, self._name, value)


class MyClass:
    x = Desc('x')
    y = Desc('y')


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
