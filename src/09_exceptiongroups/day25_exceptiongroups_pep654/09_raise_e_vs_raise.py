# 09
try:
    raise ExceptionGroup(
        "eg",
        [
            ValueError(1),
            TypeError(2),
            OSError(3),
            ExceptionGroup(
                "nested",
                [OSError(4), TypeError(5), ValueError(6)])
        ]
    )
except* ValueError as e:
    print(f'*ValueError: {e!r}')
    raise e
except* OSError as e:
    print(f'*OSError: {e!r}')
    raise
