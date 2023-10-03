# 02c
n = 10
adders = [lambda x:x+n for n in range(1, 4)]
for adder in adders:
    print(adder(1))  # 4 4 4
