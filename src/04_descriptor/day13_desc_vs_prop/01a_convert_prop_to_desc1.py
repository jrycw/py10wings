# 01a
class MyClass:
    def __init__(self, x, y, z):
        self._x = x
        self._y = y
        self._z = z

    @property
    def x(self):
        """doc for x"""
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def z(self):
        return self._z


if __name__ == '__main__':
    my_inst = MyClass(1, 1, 1)
    print(my_inst.x)  # 1
    print(my_inst.y)  # 1
    print(my_inst.z)  # 1

    # my_inst.x = 2  # ValueError
    # my_inst.y = 2  # ValueError
    # my_inst.z = 2  # ValueError
