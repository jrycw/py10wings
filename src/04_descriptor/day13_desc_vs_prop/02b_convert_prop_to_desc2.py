# 02b
class PositiveInt:
    def __get__(self, instance, owner_cls):
        if instance is None:
            return self
        return getattr(instance, self._name)

    def __set__(self, instance, value):
        self._validate(value)
        setattr(instance, self._name, value)

    def _validate(self, value):
        if not isinstance(value, int) or value <= 0:
            raise ValueError(f'{value} is not a positive integer.')

    def __set_name__(self, owner_cls, name):
        self._name = f'_{name}'


class MyClass:
    x = PositiveInt()
    y = PositiveInt()
    z = PositiveInt()

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z


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
