# 01
class MyClass:
    def __call__(self):
        print('MyClass __call__ called because of `my_inst()`')


if __name__ == '__main__':
    my_inst = MyClass()
    my_inst()  # my_inst is callable
