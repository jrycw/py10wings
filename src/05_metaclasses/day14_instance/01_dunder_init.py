# 01
class MyClass:
    def __init__(self, x):
        self.x = x


if __name__ == '__main__':
    my_inst = MyClass(1)
    print(my_inst.__dict__)  # {'x': 1}
