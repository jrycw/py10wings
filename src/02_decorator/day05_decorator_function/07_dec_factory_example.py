# 07
import logging
from functools import wraps
from numbers import Real
from typing import get_type_hints


def log(*, to_log=True, validate_input=True):
    def dec(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if to_log:
                logging.info(
                    f' `wrapper` is called, {func=}, {args=}, {kwargs=}')
            if validate_input:
                n = len(args) + len(kwargs)
                type_hints = get_type_hints(func)
                if n and n+1 > len(type_hints):  # return is included in type_hints
                    if to_log:
                        logging.error(
                            f'Annotations={type_hints}, {args=}, {kwargs=}')
                    raise TypeError('Some annotations might be missing.')

                if args and not all(isinstance(arg, type_)
                                    for arg, type_ in zip(args, type_hints.values())):
                    if to_log:
                        logging.error(
                            f'Annotations={type_hints}, {args=}, {kwargs=}')
                    raise TypeError(
                        f'Possible incorrect type assignment in {args=}')

                # Using set might be easier?
                #
                # if kwargs and not all(isinstance(kwargs[k], type_hints[k])
                #                       for k in (set(kwargs) & set(type_hints))):
                #
                if kwargs and not all(isinstance(kw_value, type_)
                                      for name, type_ in type_hints.items()
                                      if (kw_value := kwargs.get(name))):
                    if to_log:
                        logging.error(
                            f'Annotations={type_hints}, {args=}, {kwargs=}')
                    raise TypeError(
                        f'Possible incorrect type assignment in {kwargs=}')

            result = func(*args, **kwargs)

            if validate_input:
                expected_return_type = type_hints['return']
                if not isinstance(result, expected_return_type):
                    logging.warning(
                        f' Return value: {result}(type={type(result)}) is not an ' +
                        f'instance of {expected_return_type}')
            if to_log:
                logging.info(' `wrapper` is finished.')
            return result
        return wrapper
    return dec


@log(to_log=True, validate_input=True)
def add(a: Real, b: Real) -> Real:
    """Take two reals and return their sum."""
    return a + b


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    r = add(1.2, b=3.2)
    print(r, type(r))  # 3.5, float
