import weakref


# 09
class Desc:
    def __init__(self):
        self._data = {}

    def __get__(self, instance, owner_cls):
        if instance is None:
            return self
        if value_tuple := self._data.get(id(instance)):
            return value_tuple[1]

    def __set__(self, instance, value):
        self._data[id(instance)] = (weakref.ref(
            instance, self._remove_object), value)

    def _remove_object(self, weak_ref):
        print(f'_remove_object called {weak_ref=}')
        found_key = None
        for key, (weak_ref_inst, _) in self._data.items():
            if weak_ref_inst is weak_ref:
                found_key = key
                break
        if found_key is not None:
            del self._data[found_key]


class MyClass:
    x = Desc()
    y = Desc()
    z = Desc()


if __name__ == '__main__':
    my_inst1 = MyClass()
    my_inst1.x = 1
    my_inst1.y = 2
    my_inst1.z = 3

    my_inst2 = MyClass()
    my_inst2.x = 11
    my_inst2.y = 22
    my_inst2.z = 33

    # {2462396503248: (<weakref at 0x0000023D5244A1B0; to 'MyClass' at 0x0000023D5244D4D0>, 1),
    #  2462396503504: (<weakref at 0x0000023D5244A250; to 'MyClass' at 0x0000023D5244D5D0>, 11)}
    print(MyClass.x._data)
    del my_inst1  # _remove_object called three times
