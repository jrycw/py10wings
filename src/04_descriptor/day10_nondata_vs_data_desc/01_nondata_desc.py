# 01
class NonDataDescriptor:
    def __get__(self, instance, owner_cls):
        print('NonDataDescriptor __get__ called')


class MyClass:
    non_data_desc = NonDataDescriptor()


if __name__ == '__main__':
    my_inst = MyClass()
    print(f'{my_inst.__dict__=}')  # {}
    print(f'{my_inst.non_data_desc=}')  # None
    my_inst.non_data_desc = 10  # shadow
    print(f'{my_inst.non_data_desc=}')  # 10
    print(f'{my_inst.__dict__=}')  # {'non_data_desc': 10}
    print(f'{my_inst.non_data_desc=}')  # 10
