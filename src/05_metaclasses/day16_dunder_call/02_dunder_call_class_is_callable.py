# 02
class MyType(type):
    def __call__(cls, *args, **kwargs):
        print('MyType __call__ called because of `MyClass()`')
        instance = super().__call__(*args, **kwargs)
        return instance


class MyClass(metaclass=MyType):
    def __new__(cls):
        print('MyClass __new__ called')
        instance = super().__new__(cls)
        return instance

    def __init__(self):
        print('MyClass __init__ called')

    def __call__(self):
        print('MyClass __call__ called because of `my_inst()`')


if __name__ == '__main__':
    my_inst = MyClass()  # MyClass is callable as well
    my_inst()   # my_inst is callable
