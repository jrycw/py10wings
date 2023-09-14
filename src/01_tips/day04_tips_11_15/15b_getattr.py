# 15b WRONG CODE!!!
class NonDataDesc:
    def __get__(self, instance, owner_cls):
        if instance is None:
            return self
        my_name = self._name
        return instance.my_name

    def __set_name__(self, owner_cls, name):
        self._name = f'_{name}'
