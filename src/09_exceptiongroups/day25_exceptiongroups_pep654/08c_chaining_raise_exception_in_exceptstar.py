# 08c
try:
    raise ExceptionGroup("eg", [ValueError('a')])
except* ValueError:
    raise KeyError('x')
