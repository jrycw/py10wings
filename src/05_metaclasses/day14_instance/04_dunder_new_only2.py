# 04
class MyClass:
    def __new__(cls, x):
        self = super().__new__(cls)
        self.x = x
        return self


if __name__ == '__main__':
    my_inst = MyClass(1)
    print(my_inst.__dict__)  # {'x': 1}
