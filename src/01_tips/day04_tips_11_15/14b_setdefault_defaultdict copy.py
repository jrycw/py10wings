# 14b
data = [('a', 1), ('b', 2), ('c', 3), ('a', 4)]

if __name__ == '__main__':
    d = {}
    for name, value in data:
        if name not in d:
            d[name] = []
        d[name].append(value)
