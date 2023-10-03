# 06b
try:
    try:
        raise ValueError(12)
    except* TypeError as e:
        print('never')
except ValueError as e:
    print(f'caught ValueError: {e!r}')
