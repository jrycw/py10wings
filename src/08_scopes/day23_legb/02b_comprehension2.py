# 02b
adders = []

for n in range(1, 4):
    adders.append(lambda x: x+n)

n = 10

for adder in adders:
    print(adder(1))  # 11 11 11
