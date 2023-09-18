# 03
import warnings
from functools import wraps
from textwrap import dedent

warnings.simplefilter('always', DeprecationWarning)


def warn_using_private_func(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        warn_msg = dedent('''
            Users are discouraged from directly invoking this kind of private function 
            starting with `_call`, as it is scheduled for removal in version 0.51.''')
        warnings.warn(warn_msg, DeprecationWarning)
        return fn(*args, **kwargs)
    return wrapper


def my_warn(cls):
    for name, obj in cls.__dict__.items():
        if callable(obj) and name.startswith('_call'):
            setattr(cls, name, warn_using_private_func(obj))
    return cls


@my_warn
class MyClass:
    def _call_rust(self):
        '''This function will invoke some Rust code'''


@my_warn
class MySubClass(MyClass):
    def _call_rust(self):
        '''This function will invoke some Rust code'''
        super()._call_rust()


if __name__ == '__main__':
    my_inst = MySubClass()
    my_inst._call_rust()  # warning message will show 2 times
