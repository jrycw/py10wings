# 06a
try:
    raise BlockingIOError
except* OSError as e:
    print(repr(e))
