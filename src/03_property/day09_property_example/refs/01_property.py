class MyClass:
    def __init__(self, x):
        self.x = x

    @property
    def x(self):
        # print(f'{type(self).__name__} property x getter called')
        return self._x

    @x.setter
    def x(self, value):
        # print(f'{type(self).__name__} property x setter called')
        self._x = value


class MyClass2:
    def __init__(self, x):
        self.x = x

    prop = property()

    @prop.getter
    def x(self):
        # print(f'{type(self).__name__} property x getter called')
        return self._x

    @x.setter
    def x(self, value):
        # print(f'{type(self).__name__} property x setter called')
        self._x = value


class MyClass3:
    def __init__(self, x):
        self.x = x

    def get_x(self):
        """hi"""
        return self._x

    def set_x(self, value):
        self._x = value

    x = property(fget=get_x, fset=set_x)


if __name__ == '__main__':
    c = MyClass(1)
    print(c, c.x)
    c.x = 2
    print(c, c.x)

    c2 = MyClass2(1)
    print(c2, c2.x)
    c2.x = 2
    print(c2, c2.x)

    c3 = MyClass3(1)
    print(c3, c3.x)
    c3.x = 2
    print(c3, c3.x)
    print(help(MyClass3))
