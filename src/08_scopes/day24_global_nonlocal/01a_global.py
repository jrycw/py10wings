# 01a
a = 0


def my_func():
    global a
    a += 1


my_func.a = a

my_func(), my_func()
print(my_func.a)  # 0
