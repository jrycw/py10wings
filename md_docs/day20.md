# [Day20] 七翼 - Protocols : Sequence Protocol
## 七翼大綱
接下來三天，我們介紹Python三種常用的protocols。
* [[Day20]](https://ithelp.ithome.com.tw/articles/10317772)介紹Sequence Protocol。
* [[Day21]](https://ithelp.ithome.com.tw/articles/10317773)介紹Iteration Protocol。
* [[Day22]](https://ithelp.ithome.com.tw/articles/10317774)介紹Context Manager Protocol。

## Sequence Protocol
根據[Python docs](https://docs.python.org/3/glossary.html#term-sequence)的說明，`sequence`是一個實作有`__len__`及`__getitem__`，且能以整數作為`index`取值的`iterable`。

[Sequence protocol](https://docs.python.org/3/library/functions.html#iter)有時候也被稱作[old-style iteration protocol](https://discuss.python.org/t/deprecate-old-style-iteration-protocol/17863/2)。

### `__len__`
`__len__`必須回傳整數值。它除了讓我們可以使用`len(obj)`的語法來得知`sequence`的長度外，也會在沒有實作某些`dunder method`時，和`__getitem__`聯手，提供相同的功能。

### `__getitem__`
`__getitem__`是一個有趣的`dunder method`，它讓我們能夠使用`[]`來取值，像`list`因此可以使用`整數`或`slice`作為`index`來取值，而`dict`因此可以使用`hashable`的`obj`作為`key`來取值。

### `__iter__`的備案
當`__getitem__`符合下列條件時，`sequence`可以在不實作`__iter__`的情下況，視為`iterable`。

> `index`會從0開始呼叫，當`index`在可取值範圍內回傳其值。當超出範圍時，`raise IndexError`。

這個描述非常類似`list`，而的確我們也常使用`list`作為`sequence`所真正包含的容器。


### `__contains__`的備案
[`__contains__`](https://docs.python.org/3/reference/datamodel.html#object.__contains__)是Python用來處理[membership test](https://docs.python.org/3/reference/expressions.html#membership-test-details)的`dunder method`。當使用`in obj`，而`obj`沒有實作`__contains__`，會改使用`__iter__`，如果再沒有實作`__iter__` 會改使用`__getitem__`。

### `__reversed__`的備案
[`__reversed__`](https://docs.python.org/3/reference/datamodel.html#object.__reversed__)一般被Python的`built-in` `reversed`所呼叫。當使用`reversed(obj)`，而`obj`沒有實作`__reversed__`時，會使用`__getitem___`和`__len__`來達成`reversed`的功能。

## 實例說明
`# 01`中`MySeq`是一個實作有`__getitem__`與`__len__`的`class`，所以`my_seq`可以使用`[]`來取值。
```python=
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
```
```
*****test []*****
__getitem__ called, value=0
my_seq[0]=0
```
由於我們將`__getitem__`內取值的任務`delegate`給`list`，所以符合前面"`__iter__`的備案"所述的條件，因此Python會將`my_seq`視為`iterable`。


```python=
# 01
...
if __name__ == '__main__':
    ...
    print('*****test is an iterable*****')
    for item in my_seq:
        pass
```
```
*****test is an iterable*****
__getitem__ called, value=0
__getitem__ called, value=1
__getitem__ called, value=2
__getitem__ called, value=3
<class 'IndexError'> list index out of rang
```
我們也可以觀察，當`index=3`時，因為超過了`my_seq`能接收的範圍，`self._list`會報錯，而其錯誤型態的確為`IndexError`。
```python=
# 01
...
if __name__ == '__main__':
    ...
    print('*****test in operator*****')
    print(f'{2 in my_seq=}')
```
```
*****test in operator*****
__getitem__ called, value=0
__getitem__ called, value=1
__getitem__ called, value=2
2 in my_seq=True
```
由於`my_seq`沒有實作`__contains__`與`__iter__`，所以Python會依靠`__getitem__`逐個取值，來比對2有沒有在`my_seq`中。

```python=
# 01
...
if __name__ == '__main__':
    ...
    print('*****test is reversible*****')
    for i in reversed(my_seq):  
        pass
```
```
*****test is reversible*****
__len__ called
__getitem__ called, value=2
__getitem__ called, value=1
__getitem__ called, value=0
```
由於`my_seq`沒有實作`__reversed__`，所以Python會同時使用`__getitem__`及`__len__`來達成`reversed`的功能。

## collections.abc
Python的[collections.abc](https://docs.python.org/3/library/collections.abc.html)中有`Sequence`及`MutableSequence`兩種`abstract base class`，方便我們繼承使用。文件中有說明我們必須實作哪些`dunder method`，而根據這些`dunder method`，Python將能自動提供其它額外的`method`可以使用。

如果繼承`Sequence`的話，只需要實作`__getitem__`與`__len__`，就能額外獲得`__contains__`、`__iter__`、`__reversed__`、`index`與`count`。

如果繼承`MutableSequence`的話，只需要實作`__getitem__`、 `__setitem__`、`__delitem__`、`__len__`與`insert`，就能獲得繼承
`Sequence`額外獲得的`method`加上`append`、`reverse`、`extend`、`pop`、`remove`與 `__iadd__`。

## 當日筆記
雖然只實作`__getitem__`與`__len__`，就可以作為很多`dunder method`的備案，但是依靠`__getitem__`逐個取值的效率是比較差的。所以如果可能的話，我們會建議針對各種`dunder method`實作比較有效率的邏輯。

## 參考資料
* [Python for network engineers - VI. Basics of object-oriented programming - 23. Special methods - Protocols - Sequence protocol](https://pyneng.readthedocs.io/en/latest/book/23_oop_special_methods/sequence_protocol.html)。

## Code
[本日程式碼傳送門](https://github.com/jrycw/py10wings/tree/master/src/07_protocols/day20_sequence_protocol)。