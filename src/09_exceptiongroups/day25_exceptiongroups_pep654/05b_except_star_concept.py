# 05b
class SpamError(Exception):
    ...


class FooError(Exception):
    ...


class BarError(Exception):
    ...


class BazError(Exception):
    ...


eg = ExceptionGroup('msg', [FooError(1), FooError(2), BazError()])

# try:
unhandled = eg

# except* SpamError:
match, rest = unhandled.split(SpamError)
print(f'{match=}, {rest=}')
unhandled = rest

# except* FooError as e:
match, rest = unhandled.split(FooError)
print(f'{match=}, {rest=}')
unhandled = rest

# except* (BarError, BazError) as e:
match, rest = unhandled.split((BarError, BazError))
print(f'{match=}, {rest=}')
