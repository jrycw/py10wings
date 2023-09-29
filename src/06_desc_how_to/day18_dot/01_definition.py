# 01
class NonDataDescriptor:
    def __get__(self, instance, owner_cls):
        ...


class DataDescriptor:
    def __get__(self, instance, owner_cls):
        ...

    def __set__(self, instance, value):
        ...


class DummyClass:
    a = 1


class MyClass(DummyClass):
    non_data_desc = NonDataDescriptor()
    data_desc = DataDescriptor()


if __name__ == '__main__':
    print(MyClass.__mro__)  # MyClass, DummyClass, object
    my_inst = MyClass()
