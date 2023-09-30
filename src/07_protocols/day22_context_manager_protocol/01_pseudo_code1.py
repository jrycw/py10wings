# 01 PSEUDO CODE!!!
class Object:
    def __init__(self, **kwargs): ...
    def start(self): ...
    def finish(self): ...


class MyContextManager:
    def __init__(self, **kwargs):
        self._kwargs = kwargs

    def _make_obj(self, **kwargs):
        return Object(**kwargs)

    def setup(self):
        """set up something and possibly call self._obj.start() to do something"""
        self._obj = self._make_obj(**self._kwargs)
        self._obj.start()

    def cleanup(self):
        """Possibly call self._obj.finish() to do something and clean-up something"""
        self._obj.finish()

    def __enter__(self):
        self.setup()
        # can:
        # 1. return self
        # 2. return self._obj
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # may need to handle exceptions
        self.cleanup()
