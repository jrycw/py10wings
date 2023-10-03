# 07b
try:
    raise TypeError(1)
except* TypeError:
    raise ValueError(2) from None  # <- not caught in the next clause
except* ValueError:
    print('never')
