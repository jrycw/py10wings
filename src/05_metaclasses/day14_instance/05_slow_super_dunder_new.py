# 05
import time


class SlowNewClass:
    def __new__(cls,  **kwargs):
        time.sleep(1)
        return super().__new__(cls)

    def __init__(self, **kwargs):
        self.__dict__.update(**kwargs)


class MyClass(SlowNewClass):
    def __init__(self, **kwargs):
        if all(value >= 0 for value in kwargs.values()):
            if x := kwargs.pop('x', None):
                self.x = x+100
            super().__init__(**kwargs)
        else:
            raise ValueError


class MyClass2(SlowNewClass):
    def __new__(cls, **kwargs):
        if all(value >= 0 for value in kwargs.values()):
            return super().__new__(cls, **kwargs)
        raise ValueError

    def __init__(self, **kwargs):
        if x := kwargs.pop('x', None):
            self.x = x+100
        super().__init__(**kwargs)


def timer(cls, **kwargs):
    try:
        start = time.perf_counter()
        my_inst = cls(**kwargs)
    except ValueError:
        pass
    finally:
        end = time.perf_counter()
        elapsed = end - start
        print(f'{elapsed=:.6f} secs for {cls}')


if __name__ == '__main__':
    my_inst = MyClass(x=1, y=2)
    print(my_inst.__dict__)  # {'x': 101, 'y': 2}

    my_inst2 = MyClass2(x=1, y=2)
    print(my_inst2.__dict__)  # {'x': 101, 'y': 2}

    print('normal: ')
    timer(MyClass, x=1, y=2)  # 1.000700
    timer(MyClass2, x=1, y=2)  # 1.000952

    print('exceptions: ')
    timer(MyClass, x=-1, y=2)  # 1.000298
    timer(MyClass2, x=-1, y=2)  # 0.000011
