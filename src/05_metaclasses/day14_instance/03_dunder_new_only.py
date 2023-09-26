# 03
class MyClass:
    def __new__(cls, x):
        instance = super().__new__(cls)
        instance.x = x
        return instance


if __name__ == '__main__':
    my_inst = MyClass(1)
    print(my_inst.__dict__)  # {'x': 1}
