# 02a
n = 10
adders = []

for n in range(1, 4):
    adders.append(lambda x: x+n)

for adder in adders:
    print(adder(1))  # 4 4 4
