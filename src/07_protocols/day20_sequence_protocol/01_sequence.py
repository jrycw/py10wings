# 01
class MySeq:
    def __init__(self, iterable):
        self._list = list(iterable)

    def __len__(self):
        print('__len__ called')
        return len(self._list)

    def __getitem__(self, value):
        print(f'__getitem__ called, {value=}')
        try:
            return self._list[value]
        except Exception as e:
            print(type(e), e)
            raise


if __name__ == '__main__':
    my_seq = MySeq(range(3))

    print('*****test []*****')
    print(f'{my_seq[0]=}')  # 0

    print('*****test is an iterable*****')
    for item in my_seq:  # like impl `__iter__`, but slower
        pass

    print('*****test in operator*****')
    print(f'{2 in my_seq=}')  # True, like impl `__contains__ `, but slower

    print('*****test is reversible*****')
    for i in reversed(my_seq):  # like impl `__reversed__ `, but slower
        pass
