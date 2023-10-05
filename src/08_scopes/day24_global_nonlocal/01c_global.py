# 01c
a = 0
print(f'Begin: {id(a)=}')
print(f'{id(0)=}')


def my_func():
    global a
    print(f'Begin(my_func): {id(a)=}')
    a += 1
    print(f'End(my_func): {id(a)=}')


def get_a():
    return a


my_func.a = get_a
my_func(), my_func()
print(f'{my_func.a()=}')  # 2
print(f'{a=}')  # 2
print(f'{id(my_func.a())=}')
print(f'End: {id(a)=}')
