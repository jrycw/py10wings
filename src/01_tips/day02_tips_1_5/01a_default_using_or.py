# 01a
class MyClass:
    def __init__(self, x=None):
        self.x = x or 'x'


if __name__ == '__main__':
    my_inst = MyClass(False)
    print(my_inst.x)  # 'x' (not False)
