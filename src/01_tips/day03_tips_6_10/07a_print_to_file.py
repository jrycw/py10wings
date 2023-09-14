# 07a
text = ['abcde', '12345']

with open('file1.txt', 'w') as f:
    for s in text:
        f.write(s+'\n')
