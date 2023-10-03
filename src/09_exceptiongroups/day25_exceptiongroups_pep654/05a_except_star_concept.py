# 05a
import traceback


class SpamError(Exception):
    ...


class FooError(Exception):
    ...


class BarError(Exception):
    ...


class BazError(Exception):
    ...


eg = ExceptionGroup('msg', [FooError(1), FooError(2), BazError()])
try:
    raise eg
except* SpamError:
    ...
except* FooError as e:
    print('Handling FooError: ')
    traceback.print_exception(e)
except* (BarError, BazError) as e:
    print('Handling (BarError, BazError): ')
    traceback.print_exception(e)
