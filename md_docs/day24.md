# [Day24] 八翼 - Scopes：常見錯誤2（global與nonlocal）
在使用`global`與`nonlocal`時，有一個常見的錯誤，我們以兩個例子來說明。

## `global`
### 問題觀察
`# 01a`中：
* 生成一個`a`變數於`G`，其值為`0`。
* 定義一個`function` `my_func`，於其中使用`global a`後，並將`a`加上`1`。
* 使用`my_func.a`，設定`my_fuc`的`a`為`a`。
* 連續呼叫`my_func`兩次。

此時，觀察`my_func.a`，會發現其值為`0`，而不是預期的`2`，您能看出為什麼嗎？
```python=
# 01a
a = 0


def my_func():
    global a
    a += 1


my_func.a = a

my_func(), my_func()
print(f'{my_func.a=}')  # 0
print(f'{a=}')  # 2
```
這是因為`my_func.a = a`將`my_func.a`指到`a`，這個`a`就是一開始`a=0`的`a`，而`a`又指到`0`。後來呼叫`my_func`，只會讓`a`這個符號指到新計算出來的值，是一個新的記憶體位置。

我們可以藉由印出各階段`a`的記憶體位置來確認。
```python=
# 01b
a = 0
print(f'Begin: {id(a)=}')
print(f'{id(0)=}')


def my_func():
    global a
    print(f'Begin(my_func): {id(a)=}')
    a += 1
    print(f'End(my_func): {id(a)=}')


my_func.a = a
my_func(), my_func()
print(f'{my_func.a=}')  # 0
print(f'{a=}')  # 2
print(f'{id(my_func.a)=}')
print(f'End: {id(a)=}')
```
```
Begin: id(a)=140726095700744
id(0)=140726095700744
Begin(my_func): id(a)=140726095700744
End(my_func): id(a)=140726095700776
Begin(my_func): id(a)=140726095700776
End(my_func): id(a)=140726095700808
my_func.a=0
a=2
id(my_func.a)=140726095700744
End: id(a)=140726095700808
```
我們可以看出`my_func.a`與最終`a`的記憶體位置不一致。

### 解決方法
我們需要一個`get_a` `function`作為`my_func.a`。當`get_a`被執行時，可以取得已經是`global`的`a`。只是這麼一來，我們不能使用`my_func.a`，而必須使用`my_func.a()`才能取得`a`。
```python=
# 01c
a = 0
print(f'Begin: {id(a)=}')
print(f'{id(0)=}')


def my_func():
    global a
    print(f'Begin(my_func): {id(a)=}')
    a += 1
    print(f'End(my_func): {id(a)=}')


def get_a():
    return a


my_func.a = get_a
my_func(), my_func()
print(f'{my_func.a()=}')  # 2
print(f'{a=}')  # 2
print(f'{id(my_func.a())=}')
print(f'End: {id(a)=}')
```
```
Begin: id(a)=140726095700744
id(0)=140726095700744
Begin(my_func): id(a)=140726095700744
End(my_func): id(a)=140726095700776
Begin(my_func): id(a)=140726095700776
End(my_func): id(a)=140726095700808
my_func.a()=2
a=2
id(my_func.a())=140726095700808
End: id(a)=140726095700808
```
我們可以看出`my_func.a()`與最終`a`的記憶體位置是一致的。


## `nonlocal`
這個小節我們準備實作一個`decorator`，其可以有一個`attribute`或`function`告知我們，被裝飾的`function`被呼叫了幾次。
### 問題觀察
`# 02a`中：
* 定義一個`decorator function` `my_counter`。
    * 於`my_counter`中定義`count=0`。
    * 在`wrapper`中對`count`使用`nonlocal`的關鍵字，並將`counts`加上`1`。
    * 回傳`fn`搭配`*args`與`**kwargs`呼叫結果。
    * 使用`wrapper.counts = counts`，設定`wrapper`的`counts` 為`counts`。
    * 最後回傳`wrapper`。
    * 將`my_counter`裝飾在`my_func`上。
    * 連續呼叫`my_func`兩次。

此時，觀察`my_func.counts`，會發現其值為`0`，而不是預期的`2`，相信這次聰明的您，應該知道問題在哪了吧？

其實原因跟上面小題是類似的，`wrapper.counts`是指著一開始的`counts`，而`counts`指的是`0`。
```python=
# 02a
from functools import wraps


def my_counter(fn):
    counts = 0

    @wraps(fn)
    def wrapper(*args, **kwargs):
        nonlocal counts
        counts += 1
        return fn(*args, **kwargs)

    wrapper.counts = counts
    return wrapper


@my_counter
def my_func():
    pass


my_func(), my_func()
print(my_func.counts)  # 0
```
接下來，我們分別使用`decorator function`及`decorator class`兩種方法來試著解決問題。

### 解決方法1
`# 02b`我們使用了和上面小題類似的解法，用一個`get_counts` `function`來取得`nonlocal`的`counts`。
```python=
# 02b
from functools import wraps


def my_counter(fn):
    counts = 0

    @wraps(fn)
    def wrapper(*args, **kwargs):
        nonlocal counts
        counts += 1
        return fn(*args, **kwargs)

    def get_counts():
        return counts

    wrapper.counts = get_counts
    return wrapper


@my_counter
def my_func():
    pass


my_func(), my_func()
print(my_func.counts())  # 2
```
`方法1`在呼叫兩次`my_func()`後，可以順利取得`2`。請注意，如果採用這個方法，我們必須使用`my_func.counts()`來取得`counts`。

### 解決方法2
`# 02c`中：
* 定義一個`decorator class`為`MyCounter`。
* `__init__`接收被裝飾的`function`，存為`self._fn`。此外也順便定義了`self._count=0`，作為底層真正記錄呼叫次數的變數。
* `__call__`中我們將`self._count`加上`1`，並回傳`self._fn`搭配`__call__`所接收`args`及`kwargs`的呼叫結果。
* 定義一個`counts` `property`幫助我們回傳底層的`self._counts`。
* 將`MyCounter`裝飾在`my_func`上。
* 連續呼叫`my_func`兩次。
```python=
# 02c
class MyCounter:
    def __init__(self, fn):
        self._fn = fn
        self._counts = 0

    def __call__(self, *args, **kwargs):
        self._counts += 1
        return self._fn(*args, **kwargs)

    @property
    def counts(self):
        return self._counts


@MyCounter
def my_func():
    pass


my_func(), my_func()
print(my_func.counts)  # 2
```
`解決方法2`在呼叫兩次`my_func()`後，也可以順利取得`2`。請注意，如果採用這個方法，可以使用`my_func.counts`來取得`counts`(謝謝`property`)。

### 解決方法比較
`decorator function`是一般人比較熟悉的，大部份情況，我們也會優先使用`decorator function`，因為實作起來比較直觀。但是如果當`decorator function`中使用很多的`nonlocal`時（有許多狀態需要儲存），或許改用`decorator class`會是比較好的方法。在這種情況下，`解決方法2`比`解決方法1`簡潔不少，而且`解決方法2`還可以使用`my_func.counts`取值，不必像`解決方法1`一樣得使用`my_func.counts()`。


## 當日筆記
* 使用`global`時與`nonlocal`關鍵字時，必須細心確認。
* 當`decorator`內有很多狀態需要儲存時，實作`decorator class`或許會比`decorator function`來得方便。

## 參考資料
本日內容大多收集整理自[Python 3:Deep Dive](https://github.com/fbaptiste/python-deepdive)。其中`nonlocal`的範例可以參考[Part 4-Section 04-Polymorphism and Special Methods- 06 Callables](https://github.com/fbaptiste/python-deepdive/blob/main/Part%204/Section%2004%20-%20Polymorphism%20and%20Special%20Methods/06%20-%20Callables.ipynb)，會有更詳細的說明。


## Code
[本日程式碼傳送門](https://github.com/jrycw/py10wings/tree/master/src/08_scopes/day24_global_nonlocal)。