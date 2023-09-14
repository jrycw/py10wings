# 07d
with (open('file1.txt') as f1,
      open('file2.txt') as f2,
      open('file3.txt') as f3):
    print(f1.read() == f2.read() == f3.read())  # True
