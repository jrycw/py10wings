# 02
class MyClass:
    def __new__(cls, x):
        instance = super().__new__(cls)
        print(f'{id(instance)=}')
        return instance

    def __init__(self, x):
        print(f'{id(self)=}')
        self.x = x


if __name__ == '__main__':
    my_inst = MyClass(1)
    print(my_inst.__dict__)  # {'x': 1}
