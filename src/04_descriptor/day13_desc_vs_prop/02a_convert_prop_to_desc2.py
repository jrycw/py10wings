# 02a
class MyClass:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        self._validate(value)
        self._x = value

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        self._validate(value)
        self._y = value

    @property
    def z(self):
        return self._z

    @z.setter
    def z(self, value):
        self._validate(value)
        self._z = value

    def _validate(self, value):
        if not isinstance(value, int) or value <= 0:
            raise ValueError(f'{value} is not a positive integer.')


if __name__ == '__main__':
    my_inst = MyClass(1, 1, 1)
    print(my_inst.x)  # 1
    print(my_inst.y)  # 1
    print(my_inst.z)  # 1

    my_inst.x = 2
    my_inst.y = 2
    my_inst.z = 2
    print(my_inst.x)  # 2
    print(my_inst.y)  # 2
    print(my_inst.z)  # 2

    # my_inst.x = 0  # ValueError
    # my_inst.y = -1  # ValueError
    # my_inst.z = -2.2  # ValueError
