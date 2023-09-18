# 101
class MyClass:
    def __init__(self, x):
        self.set_x = x  # not self.x = x

    @property
    def x(self):
        """docstrings from fget"""
        return self._x

    @x.setter
    def set_x(self, value):
        self._x = value

    @x.deleter
    def del_x(self):
        del self._x


if __name__ == '__main__':
    my_inst = MyClass(1)
    for name, prop in (('x', MyClass.x),
                       ('set_x', MyClass.set_x),
                       ('del_x', MyClass.del_x)):
        print(f'prop {name=}: ')
        print(f'type of prop {name} is {type(prop)}')
        print(f'fget={prop.fget}')
        print(f'fset={prop.fset}')
        print(f'fdel={prop.fdel}')
        print(f'doc={prop.__doc__}\n')
