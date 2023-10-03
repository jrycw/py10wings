# 02f
n = 10
adders = [lambda x, n=n:x+n for n in range(1, 4)]
for adder in adders:
    print(adder(1))  # 2 3 4
