# 08a
try:
    raise ExceptionGroup("one", [ValueError('a'), TypeError('b')])
except* ValueError:
    raise ExceptionGroup("two", [KeyError('x'), KeyError('y')])
