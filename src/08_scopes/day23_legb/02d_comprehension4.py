# 02d
adders = [lambda x:x+n for n in range(1, 4)]
n = 10
for adder in adders:
    print(adder(1))  # 4 4 4
