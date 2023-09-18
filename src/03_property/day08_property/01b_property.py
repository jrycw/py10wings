# 01b
class MyClass:
    def __init__(self, x):
        self.x = x

    def get_x(self):
        return self._x

    def set_x(self, value):
        self._x = value

    def del_x(self):
        del self._x

    x = property(fget=get_x,
                 fset=set_x,
                 fdel=del_x,
                 doc="""docstrings""")
