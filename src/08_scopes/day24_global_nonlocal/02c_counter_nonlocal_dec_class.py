# 02c
class MyCounter:
    def __init__(self, fn):
        self._fn = fn
        self._counts = 0

    def __call__(self, *args, **kwargs):
        self._counts += 1
        return self._fn(*args, **kwargs)

    @property
    def counts(self):
        return self._counts


@MyCounter
def my_func():
    pass


my_func(), my_func()
print(my_func.counts)  # 2
