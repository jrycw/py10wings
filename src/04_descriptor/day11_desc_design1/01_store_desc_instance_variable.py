# 01
class Desc:
    def __get__(self, instance, owner_cls):
        return self._value

    def __set__(self, instance, value):
        self._value = value


class MyClass:
    x = Desc()


if __name__ == '__main__':
    my_inst1, my_inst2 = MyClass(), MyClass()

    # my_inst1
    my_inst1.x = 1
    print(f'{my_inst1.x=}')  # 1

    # my_inst2
    print(f'{my_inst2.x=}')  # 1
    my_inst2.x = 2
    print(f'{my_inst2.x=}')  # 2

    # my_inst1.x also changed
    print(f'{my_inst1.x=}')  # 2...not 1
