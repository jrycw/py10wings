# 01
import traceback

eg = ExceptionGroup(
    "one",
    [
        TypeError(1),
        ExceptionGroup(
            "two",
            [TypeError(2), ValueError(3)]
        ),
        ExceptionGroup(
            "three",
            [OSError(4)]
        )
    ]
)
if __name__ == '__main__':
    traceback.print_exception(eg)

    type_errors = eg.subgroup(lambda e: isinstance(e, TypeError))
    traceback.print_exception(type_errors)

    match, rest = eg.split(lambda e: isinstance(e, TypeError))
    traceback.print_exception(match)
    traceback.print_exception(rest)

    type_errors2 = eg.subgroup(TypeError)
    match, rest = eg.split(TypeError)

    type_errors3 = eg.subgroup((TypeError,))
    match, rest = eg.split((TypeError,))
