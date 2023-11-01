# [Day23] 八翼 - Scopes：常見錯誤1（LEGB原則）

## 八翼大綱
Python尋找變數的方法是透過`LEGB`，即`Local`、`Enclosing`、`Global`及`Built-in` scope，來層層尋找。有興趣深究的朋友，可以參考這篇[Real Python的講解](https://realpython.com/python-scope-legb-rule)。

雖然概念是清楚的，但仍然有一些需要注意的地方。本翼中，我們將分別以`L`、`E`、`G`及`B`來代稱`Local`、`Enclosing`、`Global`及`Built-in` scope。

* [[Day23]](https://ithelp.ithome.com.tw/articles/10317775) 常見錯誤1（LEGB原則）。
* [[Day24]](https://ithelp.ithome.com.tw/articles/10317776) 常見錯誤2（global與nonlocal）。

## UnBoundLocalError
`UnBoundLocalError`是一個常見的錯誤。`# 01`中，當`unboundlocalerror_func`被呼叫時，會`raise UnboundLocalError`。您可能會覺得疑惑，覺得`print(x)`會因為找不到`L`的`x`，而`unboundlocalerror_func`又沒有`E`，所以會在`G`中來尋找`x`，為什麼會報錯呢？

這是因為在`unboundlocalerror_func`有`x = 2`這個`assignment`。Python是在execute（或是想成compile）時就決定一個變數是不是`local variable`。由於`unboundlocalerror_func`中我們有指定`x`為`2`，Python於execute（或compile）階段就會先認定`x`是一個`local variable`。接著當我們真正呼叫`unboundlocalerror_func`時，Python會開始依照`LEGB`的原則尋找變數。由於`x`已被認定是一個`local variable`，所以Python只會在`unboundlocalerror_func`這個`L`中尋找`x`，而我們的確於定義`x`前，就使用了`print(x)`，所以會報錯。

```python=
# 01
x = 1


def unboundlocalerror_func():
    print(x)
    x = 2


unboundlocalerror_func()  # UnboundLocalError
``` 

## Comprehension
在使用各種`Comprehension`時，也是一個容易出錯的地方。我們透過一連串小例子，慢慢說明。

### 暖身一下
`# 02a`中，當我們真正呼叫`adders`中每一個`adder`時，Python會依照`LEGB`原則尋找`n`。由於在`L`找不到`n`，又沒有`E`，最後在`G`中找到`n`，其值為`3`（不是`10`），因為在`for n in range(1, 4)`中，`n`最後於`G`中被指為`3`。
```python=
# 02a
n = 10
adders = []

for n in range(1, 4):
    adders.append(lambda x: x+n)

for adder in adders:
    print(adder(1))  # 4 4 4
```

如果能理解`# 02a`的話，`# 02b`也是相同概念，最後於`G`中的`n`值為10。
```python=
# 02b
adders = []

for n in range(1, 4):
    adders.append(lambda x: x+n)

n = 10

for adder in adders:
    print(adder(1))  # 11 11 11
```

### list comprehension
我們將`# 02a`以list comprehension的方式改寫為`# 02c`，答案不變。
```python=
# 02c
n = 10
adders = [lambda x:x+n for n in range(1, 4)]
for adder in adders:
    print(adder(1))  # 4 4 4
```
但當我們將`# 02b`改寫為`# 02d`時，答案卻變了，這可能會讓你有點驚訝。
```python=
# 02d
adders = [lambda x:x+n for n in range(1, 4)]
n = 10
for adder in adders:
    print(adder(1))  # 4 4 4
```
事實上，comprehesion內就像一個小的`local` scope（或可以想成一個`namespace`），`# 02c`與`# 02d`可以改寫為`# 02e`，至於`n = 10`放前放後，並不影響答案。
```python=
# 02e
n = 10


def get_adders():
    adders = []
    for n in range(1, 4):
        def my_func(x):
            return x+n
        adders.append(my_func)
    return adders


adders2 = get_adders()
for adder in adders2:
    print(adder(1))  # 4 4 4
```
當我們呼叫每個`adder`時，由於`L`中找不到`n`，所以我們是在`E`這層找到`n`，其值為`3`，因為`for n in range(1, 4)`在最後將`n`指為`3`。

### 修正寫法
如果我們想要每個`adder`都能獲得不同的`n`值，`# 02f`是一個可以參考的寫法。我們將n定義為`lambda`的`keyword argument`，並預設其值為`n`。這麼一來，於迴圈中我們就可以接受不同的`n`值了。
```python=
# 02f
n = 10
adders = [lambda x, n=n:x+n for n in range(1, 4)]
for adder in adders:
    print(adder(1))  # 2 3 4
```

## Class Body
由` class body`內取得變數時，也是一個容易讓人搞糊塗的地方，我們透過`# 03`來了解。
```python=
# 03
fruit = 'Apple'


class Basket:
    fruit = 'Orange'
    partition1 = [fruit] * 3
    partition2 = [fruit for _ in range(3)]

    def get_fruit(self):
        return f'{fruit}'


basket = Basket()
print(basket.get_fruit())  # Apple
print(basket.fruit)  # Orange
print(Basket.partition1)  # ['Orange', 'Orange', 'Orange']
print(basket.partition2)  # ['Apple', 'Apple', 'Apple']
```
* `basket.get_fruit()`會返回`Apple`不是`Orange`，因為在`function`內，如果要取得`class`或`instance`的`variable`時，要使用類似`self`或`cls`等語法。所以當呼叫`basket.get_fruit()`時，`L`找不到`fruit`，又沒有`E`，所以找到的是`G`的`Apple`。
* `basket.fruit`會返回`Orange`，因為`basket.__dict__`中並沒有`fruit`，所以`basket.fruit`會往上到`Basket`中尋找。此時於`Basket`有找到`fruit`，所以返回其值。
* `Basket.partition1`會返回`['Orange', 'Orange', 'Orange']`。`Basket.__dict__`中有找到`partition1`，所以返回其值。由於`partition1`與`fruit`同是`class variable`，所以`[fruit] * 3`實際上是將`fruit`其連續三次置入`list`中。
* `basket.partition2`會返回`['Apple', 'Apple', 'Apple']`。因為`basket.__dict__`中並沒有`partition2`，所以`basket.partition2`會往上到`Basket`中尋找。此時於`Basket`找到`partition2`，所以返回其值。由於`partition2`使用`list comprehension`，所以相當於其在一個`function`底下，情況跟`get_fruit`是非常類似的，所以其最後找到的是，也會是`G`的`Apple`。

## 牛刀小試
今天最後，我們來一個`metaclasses`與`scope`的綜合練習題。

### 題意
寫一個`metaclasses`來生成如`TargetClass`的`class`。
* `__init__`接受任意數目的`**kwargs`。
* 自動將`kwargs`中的`key`加上`_(underscore）`後，設為`instance variable`，其值為原`key`所相對應的`value`。
* 自動以`kwargs`中的`key`，建立`property`，並返回相對應加上`_(underscore）`的`instance variable`。
```python=
# 04
class TargetClass:
    def __init__(self, **kwargs):
        """
        kwargs: {'x': 1, 'y':2, ...}
        """
        self.__dict__.update({f'_{k}': v for k, v in kwargs.items()})

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    ...
```
### 解題思路
* 首先我們讓`MyType1`繼承`type`。
* 於`MyType1.__new__`中使用`super().__new__`生成`cls`
* 建立一個`init function`，其內部邏輯與上述`TargetClass.__init__`相同，並指定給`cls.__init__`。
* 針對`kwargs`打個迴圈，將其`key`依續設為`property`，並返回相對應的底層加上`_(underscore)`的`instance variable`。
* 最後回傳`cls`。

這麼一來我們就可以使用`MyType1`作為`MyClass1`的`metaclass`，並搭配`kwds`作為`MyType1.__new__`的最後一個參數`**kwargs`，來生成`MyClass1`，及使用`my_inst1 = MyClass1(**kwds)`生成`my_inst1`。
```python=
# 04
class MyType1(type):
    def __new__(mcls, cls_name, cls_bases, cls_dict, **kwargs):
        cls = super().__new__(mcls, cls_name, cls_bases, cls_dict)

        def init(self, **kwargs):
            self.__dict__.update({f'_{k}': v for k, v in kwargs.items()})
        cls.__init__ = init
        for prop in kwargs:
            setattr(cls,
                    prop,
                    property(lambda self: getattr(self, f'_{prop}')))
        return cls
    
    
kwds = {'x': 1, 'y': 2}


class MyClass1(metaclass=MyType1, **kwds):
    pass

my_inst1 = MyClass1(**kwds)

...
```
但是如果觀察`my_inst1.x`與`my_inst1.y`，卻發現其值都為`2`，請問您有看出問題在哪嗎？
```python=
>>> vars(my_inst1)  # {'_x': 1, '_y': 2}
>>> my_inst1.x, my_inst1.y  # 2 2
```
問題出在`property(lambda self: getattr(self, f'_{prop}'))`。`lambda self: getattr(self, f'_{prop}'`是一個`getter function`，其接收的`prop`參數，是由`for prop in kwargs`而來。當我們真正使用`my_inst1.x`及`my_inst1.y`時，每個`getter`都會先在`L`中找`prop`，因為找不到，所以往外找。最後在`E`中找到`prop`，並認為`prop`是`kwargs`的最後一個`key`。

### 修正解法
修正解法是使用`keyword arguments`，將`property(lambda self: getattr(self, f'_{prop}'))`改為`property(lambda self, attr=prop: getattr(self, f'_{attr}'))`。整體思路是與`# 02f`類似的，只是因為在`metaclass`內，語法比較複雜而已。

```python=
# 04
...

class MyType2(type):
    def __new__(mcls, cls_name, cls_bases, cls_dict, **kwargs):
        cls = super().__new__(mcls, cls_name, cls_bases, cls_dict)

        def init(self, **kwargs):
            self.__dict__.update({f'_{k}': v for k, v in kwargs.items()})
        cls.__init__ = init
        for prop in kwargs:
            setattr(cls,
                    prop,
                    property(lambda self, attr=prop: getattr(self, f'_{attr}')))
        return cls

kwds = {'x': 1, 'y': 2}

    
class MyClass2(metaclass=MyType2, **kwds):
    pass

my_inst2 = MyClass2(**kwds)
```
觀察`my_inst2.x`為`1`，而`my_inst2.y`為`2`，皆正確無誤。
```python=
>>> vars(my_inst2)  # {'_x': 1, '_y': 2}
>>> my_inst2.x, my_inst2.y  # 1 2
```

## 當日筆記
* 當取用不在當前scope的變數時，要特別小心，因為此變數可能會被指派為其它值或被`mutate`，而發生預期外的行為。
* 在迴圈中，指定`function`（或`lambda`）的參數時，`keyword arguments`可能是您的好幫手。

## 參考資料
* 本日內容大多收集整理自[Python 3:Deep Dive](https://github.com/fbaptiste/python-deepdive)。這些概念`Dr. Fred Baptiste`於多個單元中，都曾反覆強調。
    * 其中class body部份可以參考[Part 4-Section 02-Classes-14 Class Body Scope](https://github.com/fbaptiste/python-deepdive/blob/main/Part%204/Section%2002%20-%20Classes/14%20-%20Class%20Body%20Scope.ipynb)
    * `牛刀小試`的例題改寫自參考[Part 4-Section 14 -Metaprogramming-11 Metaprogramming Application 1](https://github.com/fbaptiste/python-deepdive/blob/main/Part%204/Section%2014%20-%20Metaprogramming/11%20-%20Metaprogramming%20Application%201.ipynb)
* [The Hitchhiker’s Guide to Python](https://docs.python-guide.org/writing/gotchas/)


## Code
[本日程式碼傳送門](https://github.com/jrycw/py10wings/tree/master/src/08_scopes/day23_legb)。