# 02 PSEUDO CODE!!!
class MyContextManager:
    def __init__(self, new_x):
        self._new_x = new_x
        self._x = 'x'

    def __enter__(self):
        self._old_x = self._x
        self._x = self._new_x
        # can:
        # 1. return self
        # 2. return self._new_x
        # 3. return None (implicitly)
        return self._new_x

    def __exit__(self, exc_type, exc_val, exc_tb):
        # may need to handle exceptions
        self._x = self._old_x  # back to original state
        del self._old_x  # delete unused variable
