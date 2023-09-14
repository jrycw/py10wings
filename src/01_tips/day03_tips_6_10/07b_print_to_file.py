# 07b
text = ['abcde', '12345']

with open('file2.txt', 'w') as f:
    for s in text:
        print(s, file=f)
