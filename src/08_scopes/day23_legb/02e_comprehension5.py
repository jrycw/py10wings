# 02e
n = 10


def get_adders():
    adders = []
    for n in range(1, 4):
        def my_func(x):
            return x+n
        adders.append(my_func)
    return adders


adders2 = get_adders()
for adder in adders2:
    print(adder(1))  # 4 4 4
