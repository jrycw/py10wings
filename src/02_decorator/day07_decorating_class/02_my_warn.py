# 02
import warnings
from functools import wraps
from textwrap import dedent


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

    def _call_zig(self):
        '''This function will invoke some Zig code'''


if __name__ == '__main__':
    my_inst = MyClass()
    my_inst._call_rust()
    my_inst._call_zig()
