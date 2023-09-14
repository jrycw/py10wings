# 01b
class MyClass:
    def __init__(self, x=None):
        self.x = x if x is not None else 'x'


if __name__ == '__main__':
    my_inst = MyClass(False)
    print(my_inst.x)  # False
