# 01
class dec:
    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kwargs):
        print(f'{args=}, {kwargs=}')
        return self.func(*args, **kwargs)


@dec
def my_func(*args, **kwargs):
    pass


if __name__ == '__main__':
    pass
