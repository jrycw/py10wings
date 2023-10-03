# 07a
try:
    raise ExceptionGroup("one", [ValueError('a')])
except* ValueError:
    raise ExceptionGroup("two", [KeyError('x')])
except* KeyError:
    print('never')
