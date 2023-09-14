# 02b
sentinel = object()


def get_given(given=sentinel, default=0):
    return default if given is sentinel else given


if __name__ == '__main__':
    print(get_given('abc'))  # 'abc'
    print(get_given(None, 2))  # None
    # We can only get 2(default) by passing sentinel to given explicitly
    print(get_given(sentinel, 2))  # 2
