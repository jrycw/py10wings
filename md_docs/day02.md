# [Day02] 初翼 - Tips : 1~5
## 初翼大綱
接下來，連續三天，我們會每天分享五個Python小技巧。
* [[Day02]](https://ithelp.ithome.com.tw/articles/10317754)分享tips 1~5。
* [[Day03]](https://ithelp.ithome.com.tw/articles/10317755)分享tips 6~10。
* [[Day04]](https://ithelp.ithome.com.tw/articles/10317756)分享tips 11~15。

## 1. default判斷語法
`# 01a`中，`x or 'x'`使用的原理為`bool(None)`會被視為`False`，所以當沒有給定預定值時，`self.x`會被設定為`'x'`，算是一種常用的語法。但這麼一來，當`x`給定任何布林值為`False`的`obj`時，Python會使用`or`之後的`'x'`來作為`self.x`，包括`None`、`False`和空的`container`等等。

```python=
# 01a
class MyClass:
    def __init__(self, x=None):
        self.x = x or 'x'


if __name__ == '__main__':
    my_inst = MyClass(False)
    print(my_inst.x)  # 'x' (not False)
```

當不確定參數是否會傳入布林值為`False`的`obj`時，我們建議使用`# 01b`中，顯性判斷其是否為`None`的語法。看起來比較不酷沒錯，但是想起那些踩坑時的痛苦，建議還是多打幾個字，畢竟`The Zen of Python`都告誡我們`Explicit is better than implicit.`。
```python=
# 01b
class MyClass:
    def __init__(self, x=None):
        self.x = x if x is not None else 'x'


if __name__ == '__main__':
    my_inst = MyClass(False)
    print(my_inst.x)  # False
```

## 2. object()作為預設值
`None`是一個不錯的預設值。但當您的程式可以接受`None`為一合法輸入值時，又該以什麼值來當預設值呢？事實上，不管你設什麼樣的值，使用者都可能會直接傳入那個值。

一個常見的方法是使用`object()`來當預設值，一般我們會稱呼這樣的用法為`sentinel`。由於每次的`sentinel`是無法預測的，所以除非於寫code時，顯性傳進這個值，才能確定這個值是由自己傳入的。

假設我們想要寫一個`get_given` `function`，其要求如下：
* 接受兩個參數`given`與`default`。
* 當顯性給予`given`時，該`function`需回傳`given`，否則即回傳`default`，而`default`之預設值為`0`。

`# 02a`中以`None`為`given`的預設值，此時當顯性給予`None`時，其仍然會回傳`2`，但這不符合我們所希望的行為。
```python=
# 02a
def get_given(given=None, default=0):
    return default if given is None else given


if __name__ == '__main__':
    print(get_given('abc'))  # 'abc'
    print(get_given(None, 2))  # 2
```
`# 02b`中以`object()`為`sentinel`來作為`given`的預設值，此時只有當顯性傳入`sentinel`給`given`時，才能打破回傳值不是給予值的情況。
```python=
# 02b
sentinel = object()


def get_given(given=sentinel, default=0):
    return default if given is sentinel else given


if __name__ == '__main__':
    print(get_given('abc'))  # 'abc'
    print(get_given(None, 2))  # None
    # We can only get 2(default) by passing sentinel to given explicitly
    print(get_given(sentinel, 2))  # 2
```

## 3. tuple作為預設值
在建立`class`的時候，常常會有一種情況是希望於`__init__`中選擇性接收一些值，來更新內部的某個`mutable`的`container`，像是`dict`、`set`或`list`等。

舉例來說，`# 03a`中的`MyDict`繼承`UserDict`(`註1`)。於`__init__`中接收一個選擇性的`dict_data`。當其不為`None`時，我們希望能將傳入的值，更新到`self`。
```python=
# 03a
from collections import UserDict


class MyDict(UserDict):
    def __init__(self, dict_data=None):
        super().__init__()
        if dict_data is not None:
            self.update(dict_data)
```
由於這樣類似的pattern很常出現，我們就開始動動腦，是不是有辦法免除這個`if`的確認呢？

首先`# 03b`試著將`dict_data`設為`{}`。修但幾勒，我們了解大家會說你怎麼可以把`mutable`的`obj`作為預設值呢？難道你沒讀過Python人必看的[The Hitchhiker's Guide to Python](https://docs.python-guide.org/writing/gotchas/#mutable-default-arguments)嗎？但仔細想想，如果沒有設一個`instance variable`給`dict_data`的話，我們「好像」沒有辦法`mutate`它(除非直接`mutate` `dict_data`)。
```python=
# 03b
from collections import UserDict


class MyDict(UserDict):
    def __init__(self, dict_data={}):
        super().__init__()
        self.update(dict_data)
```
當然，如果您寫成`# 03c`的格式，那麼我們就可以藉由`self._dict_data`來`mutate` `dict_data`。變動`d._dict_data`也會變動`d2._dict_data`，因為兩個是同一個`obj`，這樣的行為相信不是您想要的。
```python=
# 03c
from collections import UserDict


class MyDict(UserDict):
    def __init__(self, dict_data={}):
        super().__init__()
        self._dict_data = dict_data
        self.update(dict_data)


if __name__ == '__main__':
    d, d2 = MyDict(), MyDict()
    print(d._dict_data is d2._dict_data)  # True
    print(d, d2)  # {}, {}
    d._dict_data['a'] = 1
    print(d._dict_data is d2._dict_data)  # True
    print(d._dict_data, d2._dict_data)  # {'a': 1} {'a': 1}
```
`# 03d`中，使用`空tuple`來當預設值，由於`tuple`是`immutable`，所以不會有`# 03c`的情況，是一個我們覺得可以考慮的寫法，尤其是當這個變數代表`iterable`時。

```python=
# 03d
from collections import UserDict


class MyDict(UserDict):
    def __init__(self, dict_data=()):
        super().__init__()
        self._dict_data = dict_data
        self.update(dict_data)


if __name__ == '__main__':
    d, d2 = MyDict(), MyDict()
    print(d._dict_data is d2._dict_data)  # True
    print(d, d2)  # {}, {}
    d._dict_data = (1,)
    print(d._dict_data is d2._dict_data)  # False
    print(d._dict_data, d2._dict_data)  # (1,) ()
```
## 4. datetime.strftime vs f-string
當需要format`datetime`的`obj`時，一般會使用`datetime.strftime`，如`# 04a`。
```python=
# 04a
from datetime import datetime

now = datetime.now()
datetime_fmt = '%Y-%m-%d_%H:%M:%S'

if __name__ == '__main__':
    now_str = now.strftime(datetime_fmt)
    print(f'{now_str}')  # 2023-09-01_21:14:41
```

但其實`f-string`是可以認得`datetime` format所用的格式，而且使用起來更為方便。`# 04b`最後一行的`f-string`，我們使用兩層`{}`。外層`datetime` `object`的`:`後，可擺入需要format的格式。
```python=
# 04b
from datetime import datetime

now = datetime.now()
datetime_fmt = '%Y-%m-%d_%H:%M:%S'

if __name__ == '__main__':
    print(f'{now:{datetime_fmt}}')  # 2023-09-01_21:14:41
```


## 5. 以docstrings代替pass
當定義客製的`Exception`時，常使用`pass`，如`# 05a`。
```python=
# 05a
class MyError(Exception):
    pass
```

其實有時候也可以考慮使用`docstrings`代替`pass`，如`# 05b`。除了這是個合法的語法外(相當於指定`__doc__`)，也可以為`Exception`增加說明。其它像是定義需要略為說明的`class`或是`function`時，也可以使用。

```python=
# 05b
class BetterMyError(Exception):
    """This error will be raised if..."""

```
另外，一個有趣的小知識，其實[Ellipsis](https://docs.python.org/3/library/constants.html#Ellipsis)也是合法的語法，如`# 05c`。
```python=
# 05c
class MyCoolError(Exception):
    ...
```
## 備註
註1：`UserDict`相比於繼承`dict`更加容易操作，如果有興趣深入研究的朋友，可以參考[Trey的說明](https://treyhunner.com/2019/04/why-you-shouldnt-inherit-from-list-and-dict-in-python/)或是[Python docs](https://docs.python.org/3/library/collections.html#collections.UserDict)。

## Code
[本日程式碼傳送門](https://github.com/jrycw/py10wings/tree/master/src/01_tips/day02_tips_1_5)。