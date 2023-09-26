# 07
class MyStr1(str):
    def __init__(self, s):
        super().__init__(s + '_123')


class MyStr2(str):
    def __new__(cls, s):
        return super().__new__(cls,  s + '_123')


if __name__ == '__main__':
    # my_str1 = MyStr1('abc')  # TypeError
    my_str2 = MyStr2('abc')
    print(my_str2)  # 'abc_123'
