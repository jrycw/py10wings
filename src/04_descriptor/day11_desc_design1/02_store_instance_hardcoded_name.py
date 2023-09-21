# 02
class Desc:
    def __get__(self, instance, owner_cls):
        return getattr(instance, 'hardcoded_name', None)

    def __set__(self, instance, value):
        setattr(instance, 'hardcoded_name', value)


class MyClass:
    x = Desc()
    y = Desc()


if __name__ == '__main__':
    my_inst = MyClass()
    print(f'{my_inst.__dict__=}')  # {}

    my_inst.x = 1
    print(f'{my_inst.x=}')  # 1
    print(f'{my_inst.__dict__=}')  # {'hardcoded_name': 1}

    my_inst.x = 2
    print(f'{my_inst.x=}')  # 2
    print(f'{my_inst.y=}')  # 2
    print(f'{my_inst.__dict__=}')  # {'hardcoded_name': 2}
