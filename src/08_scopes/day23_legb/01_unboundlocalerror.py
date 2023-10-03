# 01
x = 1


def unboundlocalerror_func():
    print(x)
    x = 2


unboundlocalerror_func()  # UnboundLocalError
