# [Day13] 四翼 - Descriptor : property vs Descriptor
`property`內部實作了`descriptor protocol`，所以可以視其為一種簡易版，單次使用的`data descriptor`。在我們需要少量`descriptor`特性時，`property`是一個非常方便的工具。

今天假設在剛開始實作一個`class`時，我們使用了`property`快速完成了一個prototype。當我們準備進一步往下，繼續實作更多細節的時候，發現使用了很多具有相同邏輯的`property`，所以決定自己實作一個`descriptor`，將這些邏輯包起來重覆利用。

我們會練習三個小題，`練習1`是概念說明，`練習2`及`練習3`是實戰例題。我們將使用`方法6`來實作，方便大家之後可以對照[Descriptor HowTo Guide](https://docs.python.org/3/howto/descriptor.html#overview-of-descriptor-invocation)中的講解，因這兩個小題皆是受其啟發而來。

## 練習1
`# 01a`中我們定義了三個`prop`，他們的功能都是在返回其底層的`self._x`、`self._y`及`self._y`。
```python=
# 01a
class MyClass:
    def __init__(self, x, y, z):
        self._x = x
        self._y = y
        self._z = z

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def z(self):
        return self._z


if __name__ == '__main__':
    my_inst = MyClass(1, 1, 1)
    print(my_inst.x)  # 1
    print(my_inst.y)  # 1
    print(my_inst.z)  # 1

    # my_inst.x = 2  # ValueError
    # my_inst.y = 2  # ValueError
    # my_inst.z = 2  # ValueError
```

### 第一次嘗試
首先，`MyClass.__init__`中的邏輯可以使用`__set_name__`來達成。
```python=
# 01b
class myprop:
    def __set_name__(self, owner_cls, name):
        self._name = f'_{name}'
```
接著`property`的`getter`邏輯可以移至`__get__`。
```python=
# 01b
class myprop:
    ...
    def __get__(self, instance, owner_cls):
        if instance is None:
            return self
        return getattr(instance, self._name)
```
乍看我們好像完成了改寫，我們的`myprop`可以這麼使用。

```python=
# 01b
...
class MyClass:
    x = myprop()
    y = myprop()
    z = myprop()

    def __init__(self, x, y, z):
        self._x = x
        self._y = y
        self._z = z
```
但是別忘了`property`是實作了`descriptor protocol`的`data descriptor`，代表它不是只有`getteer`，也有`setter`及`deleter`。當我們沒有給予`property` `setter`或`deleter`時，如果對其進行`set`或`del`，會`raise AttributeError`。

而我們的`myprop`雖然可以正常`get`，卻也能`set`和`del`而不`raise AttributeError`，這不太符合我們希望的行為。事實上`myprop`因為只有實作`__get__`，所以是一個`non-data descriptor`。

```python=
# 01b
...
if __name__ == '__main__':
    my_inst = MyClass(1, 1, 1)
    print(my_inst.x)  # 1 from __get__
    my_inst.x = 2
    print(my_inst.__dict__)  # {'_x': 1, '_y': 1, '_z': 1, 'x': 2}
    print(my_inst.x)  # 2 from my_inst.__dict__
```
當第一次呼叫`my_inst.x`時，使用的是`myprop.__get__`，但是當我們使用了`my_inst.x = 2`，這就相當於直接在`my_inst.__dict__`加入`x`一樣。當第二次呼叫`my_inst.x`時，因為`instance.__dict__`會`shadow` `myprop.__get__`，所以我們變成從`instance.__dict__`取值了。

解決辦法是於`myprop`中實作`__set__`和`__delete__`，但卻直接`raise AttributeError`。這是一個非常容易出錯的盲點，只要能夠了解這邊，相信就能輕鬆穿梭在`property`和`descriptor`之間。
* 只實作`__get__`的 `descriptor` 是`non-data descriptor`，是有機會被`instance.__dict__`所`shadow`的。
* 有實作`__get__`加上`__set__`或`__delete__`兩種中最少一種的`descriptor`是`data descriptor`，其必定會`shadow` `instance.__dict__`。即使我們只是於`__set__`和`__delete__` `raise AttributeError`，它依然是`data descriptor`。這就像我們只給`property` `getter`，但沒有指定`setter`及`deleter`，`property`依然是一個具有`data descriptor`行為的`obj`。

### 第二次嘗試
於`# 01c`中我們實作了`__set__`及`__delete__`，並模仿`property`的錯誤訊息，直接`raise AttributeError`。另外，為了讓`myprop`更像`property`，我們可以於`__init__`中選擇性接收`doc`來作為說明文件。
```python=
# 01c
class myprop:
    def __init__(self, doc=None):
        self.__doc__ = doc

    def __get__(self, instance, owner_cls):
        if instance is None:
            return self
        return getattr(instance, self._name)

    def __set__(self, instance, value):
        name = self._name[1:]
        cls_name = type(instance).__name__
        raise AttributeError(
            f"myprop '{name}' of '{cls_name}' object has no setter")

    def __delete__(self, instance):
        name = self._name[1:]
        cls_name = type(instance).__name__
        raise AttributeError(
            f"myprop '{name}' of '{cls_name}' object has no deleter")

    def __set_name__(self, owner_cls, name):
        self._name = f'_{name}'


class MyClass:
    x = myprop()
    y = myprop()
    z = myprop()

    def __init__(self, x, y, z):
        self._x = x
        self._y = y
        self._z = z
```


## 練習2
`# 02a`中我們定義了三個`prop`，他們的功能都是:
* 給定的值需先通過`self._validate`驗證，確認為`int`且大於`0`時，才會設定給`self._x`、`self._y`及`self._y`。如果沒有通過`self.__validate`驗證，會`rasie ValueError`
* 返回其底層的`self._x`、`self._y`及`self._y`。
```python=
# 02a
class MyClass:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        self._validate(value)
        self._x = value

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        self._validate(value)
        self._y = value

    @property
    def z(self):
        return self._z

    @z.setter
    def z(self, value):
        self._validate(value)
        self._z = value

    def _validate(self, value):
        if not isinstance(value, int) or value <= 0:
            raise ValueError(f'{value} is not a positive integer.')
```
首先，根據題意，我們可以給`descriptor`取一個適合的名字，`PositiveInt`。`PositiveInt`的`__get__`和`__set_name__`與`練習1`相似。
```python=
# 02b
class PositiveInt:
    def __get__(self, instance, owner_cls):
        if instance is None:
            return self
        return getattr(instance, self._name)

    def __set_name__(self, owner_cls, name):
        self._name = f'_{name}'
```
`PositiveInt`的`__set__`及`_validate`是本題練習的重點。我們將`__set__`分成驗證與實際設定兩部份。

```python=
# 02b
class PositiveInt:
    ...
    def __set__(self, instance, value):
        self._validate(value)
        setattr(instance, self._name, value)

    def _validate(self, value):
        if not isinstance(value, int) or value <= 0:
            raise ValueError(f'{value} is not a positive integer.')
```
藉助`PositiveInt`我們可以將`# 02a`改為`# 02b`，是不是清爽不少呢?
```python=
# 02b
...
class MyClass:
    x = PositiveInt()
    y = PositiveInt()
    z = PositiveInt()

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
```
## 練習3
`練習3`和`練習2`非常像，差別是這次我們想要建立`NegativeInt`，讓我們可以在`class`中使用任意數量的`PositiveInt`與`NegativeInt`，如`# 03a`。
```python=
# 03a PSEUDO CODE!!!
class MyClass:
    x = PositiveInt()
    y = PositiveInt()
    z = NegativeInt()

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
```

由於`NegativeInt`與`PositiveInt`不同之處，只有`_validate` `function`而已。或許您會想不如讓`NegativeInt`繼承`PositiveInt`，然候覆寫`_validate` `function`。此舉雖然可行，但是不太合理，這麼一來就像是暗示`NegativeInt`是一種`PositiveInt`。

一個比較好的方法，是再往上一層建立一個`BaseValidator`，可以讓`PositiveInt`與`NegativeInt`繼承。

剛好Python有內建的`abc`模組來幫助我們完成這件事:
* `abc.ABC`不允許使用者直接使用`BaseValidator`生成`instance`，只能被其它`Validator`繼承。如果直接使用`BaseValidator`生成`instance`會`raise TypeError`。
* `abc.abstractmethod`可以提醒我們，繼承了`BaseValidator`的`Validator`必定要實作自己的`_validate` `function`，否則會於生成`Validator`的`instance`時`raise TypeError`。

```python=
# 03b
from abc import ABC, abstractmethod


class BaseValidator(ABC):
    def __get__(self, instance, owner_cls):
        if instance is None:
            return self
        return getattr(instance, self._name)

    def __set__(self, instance, value):
        self._validate(value)
        setattr(instance, self._name, value)

    def __set_name__(self, owner_cls, name):
        self._name = f'_{name}'

    @abstractmethod
    def _validate(self, value):
        pass
```
繼承了`BaseValidator`後，我們的`PositiveInt`與`NegativeInt`只要實作`_validate function`就好，於`MyClass`中的使用方法也不需改變。整體的程式碼是不是看起來更有架構也更專業了呢？
```python=
# 03b
...
class PositiveInt(BaseValidator):
    def _validate(self, value):
        if not isinstance(value, int) or value <= 0:
            raise ValueError(f'{value} is not a positive integer.')


class NegativeInt(BaseValidator):
    def _validate(self, value):
        if not isinstance(value, int) or value >= 0:
            raise ValueError(f'{value} is not a negative integer.')


class MyClass:
    x = PositiveInt()
    y = PositiveInt()
    z = NegativeInt()

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
```
### 為什麼沒有實作`__delete__`
當`property`沒有實作`deleter`卻使用了類似`del my_inst.x`的指令，其報錯為`AttributeError: property 'x' of 'MyClass' object has no deleter`。當`descriptor`沒有實作`__delete__`卻使用了類似`del my_inst.x`的指令，其報錯為`AttributeError: __delete__`。

我們於`練習1`實作`__delete__`是為了讓其報錯訊息更像`property`，如果是平常使用的話，大部份情況是不需要實作`__delete__`，這跟我們使用`property`的習慣是很像的。而且即使我們在沒有實作`__delete__`的情況下，又使用了`del my_inst.x`的指令，其報錯指令`AttributeError: __delete__`也是非常清楚，容易了解。


## Code
[本日程式碼傳送門](https://github.com/jrycw/py10wings/tree/master/src/04_descriptor/day13_desc_vs_prop)。