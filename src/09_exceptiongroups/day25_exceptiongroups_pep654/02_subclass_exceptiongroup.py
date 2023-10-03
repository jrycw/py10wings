# 02
class MyExceptionGroup(ExceptionGroup):
    def __new__(cls, message, excs, errcode):
        obj = super().__new__(cls, message, excs)
        obj.errcode = errcode
        return obj

    def derive(self, excs):
        return MyExceptionGroup(self.message, excs, self.errcode)


if __name__ == '__main__':
    eg = MyExceptionGroup("eg", [TypeError(1), ValueError(2)], 42)
    match, rest = eg.split(ValueError)
    print(f'match: {match!r}: {match.errcode}')
    print(f'rest: {rest!r}: {rest.errcode}')
