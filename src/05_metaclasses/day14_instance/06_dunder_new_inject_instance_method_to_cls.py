# 06
class MyClass:
    def __new__(cls, x: int):
        cls.hi = lambda self: 'hi'
        instance = super().__new__(cls)
        instance.x = x
        return instance
