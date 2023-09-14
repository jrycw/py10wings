# 07c
text = ['abcde', '12345']

with open('file3.txt', 'w') as f:
    print(*text, sep='\n', file=f)
