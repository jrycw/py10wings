# 02
class DataDescriptor:
    def __get__(self, instance, owner_cls):
        print('DataDescriptor __get__ called')

    def __set__(self, instance, value):
        print(f'DataDescriptor __set__ called, {value=}')


class MyClass:
    data_desc = DataDescriptor()


if __name__ == '__main__':
    my_inst = MyClass()
    print(f'{my_inst.__dict__=}')  # {}
    my_inst.__dict__['data_desc'] = 10
    print(f'{my_inst.data_desc=}')  # None
    my_inst.data_desc = 20  # always use data_desc.__set__
    print(f'{my_inst.data_desc=}')  # None
    print(f'{my_inst.__dict__=}')  # {}
