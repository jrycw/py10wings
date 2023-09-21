# 101
class MyClass:
    __slots__ = ()


class MyClass2:
    __slots__ = ('__dict__',)


if __name__ == '__main__':
    my_inst = MyClass()
    print(f'{my_inst.__dict__=}')  # AttributeError

    my_inst2 = MyClass2()
    print(f'{my_inst2.__dict__=}')  # {}
