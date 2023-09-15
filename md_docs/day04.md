今天我們繼續分享`tips 11~15`。

## 11. set的應用:在iterable_a裡卻不在iterable_b裡
當想尋找在a裡卻不在b裡的元素時，一般會寫成`# 11a`。如果`iterable_a`是有序的且順序需要維持的，或許這是個不錯的方法。
```python=
# 11a
iterable_a = range(1, 5)
iterable_b = range(3, 10)

if __name__ == '__main__':
    result = [a
              for a in iterable_a
              if a not in iterable_b]
    print(f'{result=}')  # result=[1, 2]   
```
如果`iterable_b`的數量很大，或是有重覆的元素，`# 11a`可以改成`# 11b`，這麼一來`in`的速度可以加快，也不會有重覆的元素。
```python=
# 11b
iterable_a = range(1, 5)
iterable_b = range(3, 10)

if __name__ == '__main__':
    result = [a
              for a in iterable_a
              if a not in set(iterable_b)]
    print(f'{result=}')  # result=[1, 2]
```
不過大多數情況是，我們不在意兩邊的元素順序及是否有重覆元素，這時可以直接用兩個`set`相減，如`# 11c`。
```python=
# 11c
iterable_a = range(1, 5)
iterable_b = range(3, 10)


if __name__ == '__main__':
    result = set(iterable_a) - set(iterable_b)
    print(f'{result=}')  # result={1, 2}
```
## 12. set的應用:if後接多個條件
當想找出一個集合內，其值為某幾個數時，一般會寫成`# 12a`。如果`if`後接的條件只有少數幾個，我們會覺得這是個ok的寫法。
```python=
# 12a
iterable = range(20)

if __name__ == '__main__':
    result = [item
              for item in iterable
              if item == 3 or item == 7 or item == 15]
    print(f'{result=}')  # result=[3, 7, 15]
```
但是如果條件比較多的話，我們會試著看看能不能改成`# 12b`的寫法。這麼一來，程式看起來就不會太冗長，而且`in wanted`會比多個`if`更有效率。
```python=
# 12b
iterable = range(20)

if __name__ == '__main__':
    wanted = {3, 7, 15}
    result = [item
              for item in iterable
              if item in wanted]
    print(f'{result=}')  # result=[3, 7, 15]
```

## 13. types模組
在比較舊版本的Python，當想要取得有些物件的`type`時，需要先對該物件使用`type`。例如想取得`None`的`type`，必須這麼做:
```python=
# 13
none_type1 = type(None)
```
雖然這方式可行，但總覺得好像有點旁門左道。這就像您會直接使用`int`，而不會使用像`int_type = type(1)`的語法來取得`int`這個`type`一樣。

新版Python的`types`模組，支援了各式各樣的`type`，讓我們可以直接取用。現在如果想要取得`None`的`type`，建議改成這麼做:
```python=
# 13
import types

none_type2 = types.NoneType
```
我們可以驗證兩種方法是一樣的:
```python=
# 13
print(none_type1 is none_type2)  # True
```
## 14. collections.defaultdict vs dict.setdefault
當我們有很多筆資料想要整理成`dict`，但其中作為`key`的元素，卻可能重覆時，我們一般會希望將`value`作為一個`container`，收集該`key`的每筆資訊。

`# 14a`是一個常見的寫法，但是我們覺得這樣的寫法不太好。原因是當`if name not in dict1`時，總共做了兩件事，建立`[]`以及`append value`，而在`else`裡，只做`append value`。既然`append value`是兩邊共同會做的事，為何不抽出來呢?
```python=
# 14a
data = [('a', 1), ('b', 2), ('c', 3), ('a', 4)]

if __name__ == '__main__':
    d = {}
    for name, value in data:
        if name not in d:
            d[name] = [value]
        else:
            d[name].append(value)
```
所以我們會傾向`# 14b`這樣的寫法。
```python=
# 14b
data = [('a', 1), ('b', 2), ('c', 3), ('a', 4)]

if __name__ == '__main__':
    d = {}
    for name, value in data:
        if name not in d:
            d[name] = []
        d[name].append(value)
```
此外Python的`collections.defaultdict`似乎更適合處理這類問題。`# 14c`也是屬於常見的作法。
```python=
# 14c
from collections import defaultdict

data = [('a', 1), ('b', 2), ('c', 3), ('a', 4)]

if __name__ == '__main__':
    d = defaultdict(list)
    for name, value in data:
        d[name].append(value)
```
最後，我們想分享一個比較冷門的寫法，就是直接使用`dict.setdefault`，如`# 14d`。第一次用可能會覺得有點怪。但是寫久了之後，發現相比於`defaultdict`要先import，再產生`defaultdict` `instance`才能使用，直接生成`dict`然候連續兩個`.(dot)`好像更一氣呵成。
```python=
# 14d
data = [('a', 1), ('b', 2), ('c', 3), ('a', 4)]

if __name__ == '__main__':
    d = {}
    for name, value in data:
        d.setdefault(name, []).append(value)
```
## 15. getattr適用時機
Python提供了非常方便來取得`attribute`的方法，就是我們習慣的`.(dot)`。但是當這個`attribute`名字是動態取得的，也就是無法在使用`.(dot)`前就知道時，就必須使用[getattr](https://docs.python.org/3/library/functions.html#getattr)。

一個最常見的應用就是實作`descriptor`。`# 15a`中，`__set_name__`會自動傳遞使用者於`class`中命名此`NonDataDesc` `instance`的名字，這麼一來這個名字是動態產生的，我們必須使用`getattr`，而無法使用類似`instance.self._name`語法來取值。
```python=
# 15a
class NonDataDesc:
    def __get__(self, instance, owner_cls):
        if instance is None:
            return self
        return getattr(instance, self._name)

    def __set_name__(self, owner_cls, name):
        self._name = f'_{name}'
```
或許您會覺得這只是因為`instance.self._name`中有兩個`.(dot)`，但事實上，即便用一個中間變數來取代`self._name`也不會成功。`# 15b`中我們先將`self._name`指給一個變數`my_name`，然後返回`instance.my_name`。這是一個錯誤的`descriptor`實作，因為`instance.my_name`只是請Python幫我們去找`my_name`這個`attribute`，而不是動態由使用者給定的名字。
```python=
# 15b WRONG CODE!!!
class NonDataDesc:
    def __get__(self, instance, owner_cls):
        if instance is None:
            return self
        my_name = self._name 
        return instance.my_name

    def __set_name__(self, owner_cls, name):
        self._name = f'_{name}'
```
此外，`getattr`可以指定第三個參數，為找不到`attribute`時的回傳值。

## Code
[本日程式碼傳送門](https://github.com/jrycw/py10wings/tree/master/src/01_tips/day04_tips_11_15)。