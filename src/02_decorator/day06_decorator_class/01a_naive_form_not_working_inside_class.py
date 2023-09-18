# 01a
class dec:
    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)


class MyClass:
    @dec
    def my_func(self, *args, **kwargs):
        pass


# class MyClass:
#     def my_func(self, *args, **kwargs):
#         pass
#     my_func = dec(my_func)  # my_func is an instance of dec now


if __name__ == '__main__':
    my_inst = MyClass()
    my_inst.my_func()  # TypeError
