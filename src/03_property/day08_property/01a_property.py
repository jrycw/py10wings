# 01a
class MyClass:
    def __init__(self, x):
        self.x = x

    prop = property()

    @prop.getter
    def x(self):
        """docstrings from fget"""
        return self._x

    @x.setter
    def x(self, value):
        self._x = value

    @x.deleter
    def x(self):
        del self._x
