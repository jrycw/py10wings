# 15a
class NonDataDesc:
    def __get__(self, instance, owner_cls):
        if instance is None:
            return self
        return getattr(instance, self._name)

    def __set_name__(self, owner_cls, name):
        self._name = f'_{name}'
