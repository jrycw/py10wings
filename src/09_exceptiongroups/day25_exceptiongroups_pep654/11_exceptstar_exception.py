# 11
try:
    raise ExceptionGroup("one", [ValueError('a'), TypeError('b')])
except* Exception as ex:  # This works
    print(type(ex), ex)
