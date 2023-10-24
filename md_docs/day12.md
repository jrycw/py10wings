# [Day12] 四翼 - Descriptor：Descriptor存取設計(2)

今天我們來分享一些`descriptor`的通用寫法。由於今天的方法都能通過和`方法1`及`方法2`類似的檢查，所以以下將不再特別說明。

## 方法5
`方法5`嘗試為每個`desc_instance`給定一個`name`，並將此`name`加上`_`作為`instance variable`存在`instance`中。
```python=
# 05
class Desc:
    def __init__(self, name):
        self._name = f'_{name}'

    def __get__(self, instance, owner_cls):
        if instance is None:
            return self
        return getattr(instance, self._name, None)

    def __set__(self, instance, value):
        setattr(instance, self._name, value)


class MyClass:
    x = Desc('x')
    y = Desc('y')
```

### 使用限制與缺點
* 即使我們於程式中，已經知道`desc_instance`於`my_inst`中所用的名為`x`或`y`，還是得再手動輸入一次`'x'`或`'y'`。
* 我們存於`instance`中的變數名，為`underscore`加上給定的名字。這是一個滿有討論空間的設定方法，大家都知道`underscore`暗示這是一個`private attribute`，但是我們不能保證這個名字沒有於`MyClass`中被使用。
* 我們假設`instance.__dict__`是可用的。

## 方法6
`方法6`相當於[Descriptor HowTo Guide](https://docs.python.org/3/howto/descriptor.html#overview-of-descriptor-invocation)中使用的方法，其和`方法5`類似，但是使用了`__set_name__`，這麼一來就不需要每次都手動指定名字了。`MyClass`中的`'x'`及`'y'`這兩個名字會自動傳遞給`desc_instance`。特別需要注意的是，如果在`__set_name__`中寫成`self._name = name`將會造成`RecursionError`。因為這麼一來`self._name`相當於`'x'`'或`'y'`。當`__get__`藉由`getattr(instance, self._name, None)`來取值時，就像是呼叫`my_inst.x`或`my_inst.y`，可是`x`及`y`都是`data descriptor`，其`__get__`會優先使用，這麼一來將會再次呼叫`__get__`。

```python=
# 06
class Desc:
    def __get__(self, instance, owner_cls):
        if instance is None:
            return self
        return getattr(instance, self._name, None)

    def __set__(self, instance, value):
        setattr(instance, self._name, value)

    def __set_name__(self, owner_cls, name):
        self._name = f'_{name}'
        # self._name = name will raise RecursionError


class MyClass:
    x = Desc()
    y = Desc()       
```


### 使用限制與缺點
* `方法6`解決了`方法5`的第一個問題，但是`_name`及`slots`的問題還是存在。

## 方法7
`方法7`使用了`instance.__dict__`，並直接使用傳入的`name`（即`self._name`）作為`instance.__dict__`的`key`，給定的`value`作為`instance.__dict__`的`value`。乍看好像和`方法6`有些相似，但是這樣寫完全展現了對`descriptor`的高度了解。
* 由於我們實作的是`data descriptor`，當由`instance`存取`attribute`時，會優先使用其`__get__`及`__set__`。所以我們可以直接使用其在`MyClass`中定義的名字，如`'x'`或`'y'`，而不用使用類似`'_x'`或`'_y'`。這麼一來，我們也不用擔心`'_x'`或`'_y'`是否在`MyClass`的其它地方是否有被使用。
* 請注意於`__get__`及`__set__`中，不能使用`getattr(instance, self.name, None)`或`setattr(instance, self.name, value)`，因為這樣會造成`RecursionError`，必須直接操作`instance.__dict__`。

```python=
# 07
class Desc:
    def __get__(self, instance, owner_cls):
        if instance is None:
            return self
        return instance.__dict__.get(self._name)

    def __set__(self, instance, value):
        instance.__dict__[self._name] = value

    def __set_name__(self, owner_cls, name):
        self._name = name


class MyClass:
    x = Desc()
    y = Desc()

    
if __name__ == '__main__':
    my_inst = MyClass()
    my_inst.x = 0
    print(f'{my_inst.__dict__=}')  # {'x': 0}
    print(f'{my_inst.x=}')  # 0 
```
`# 07`中，當使用`my_inst.x = 0`時，會呼叫`__set__`，透過`instance.__dict__[self._name] = value`的語法將`'x'`作為`key`，`0`為`value`放入`my_inst`的`instance dict`中（即`my_inst.__dict__`）。當我們使用`my_inst.x`時，會呼叫`__get__`，透過`instance.__dict__.get(self._name)`取回`0`。


### 使用限制與缺點
* 這是一個很優雅的實作方法，但是這個方法也是有`slots`的問題。

## 方法8
`方法8`與`方法3`幾乎一樣，差別在於這邊的`self._data`是使用`weakref.WeakKeyDictionary`而不是`dict`。`WeakKeyDictionary`顧名思義，儲存的是`weak reference`。所以此時，當我們使用`del`來刪除`instance`時，`instance`是可以被真正刪除的，且當`self._data`知道`instance`已被`gc`後，會自動刪除`weak reference`，這解決了我們頭痛的`memoey leak`問題。

```python=
from weakref import WeakKeyDictionary


# 08
class Desc:
    def __init__(self):
        self._data = WeakKeyDictionary()

    def __get__(self, instance, owner_cls):
        if instance is None:
            return self
        return self._data.get(instance)

    def __set__(self, instance, value):
        self._data[instance] = value


class MyClass:
    x = Desc()
    y = Desc()
```

### 使用限制與缺點
* `方法8`解決了`方法3`的第一個`gc`限制，但是仍然必須確定`instance`是`hashalbe`，才能作為`self._data`的`key`。
* 當`MyClass`有使用`slots`時，記得要將`__weakref__`加入`__slots__`中。

## 方法9
`方法9`是一個比較複雜的實作，我們逐個`function`解說。
* 於`__init__`中，建立一個`dict`作為倉庫，即`# 09`中的`self._data`。
* 於`__set__`中，需要決定`self._data`中`key`與`value`的型態。
    * `key`我們使用`id(instance)`，這可以解決`instance`必須要是`hashable`的問題。
    * `value`我們使用一個`tuple`。
        * 第一個元素為`weakref.ref(instance, self._remove_object)`，`weakref.ref`可以幫忙建立對`instance`的`weak reference`，並在`instance`的`strong reference`為`0`時，幫忙呼叫`self._remove_object`這個`callback function`。
        * 第二個元素為真正想要由`__get__`回傳的值。
* 於`__get__`中，開頭一樣先檢查`instance`是否為`None`，如果是`None`的話，代表是由`class`所呼叫，所以直接返回`desc_instance`。接下來我們使用`walrus operator`，來取`self._data.get(id(instance))`的回傳值。若能取到的話，代表其返回的是我們於`__set__`中所設定的`tuple`，從中取得第二個元素返回。若取不到的話，代表返回值為`None`，不做操作，並由Python隱性地返回`None`。
* 於`_remove_object`中，其接收`weakref.ref`所建的`weak reference`。我們針對`self._data.items()`打一個迴圈，從中比對是否有`instance`就是`weak reference`的情況，如果有就儲存`key`(`id(instance)`)到`found_key`。接著檢查`found_key`，當其不為`None`時，代表`self._data`中有需要刪除的`key-value pair`，我們透過`del self._data[found_key]`來刪除。


```python=
import weakref


# 09
class Desc:
    def __init__(self):
        self._data = {}

    def __get__(self, instance, owner_cls):
        if instance is None:
            return self
        if value_tuple := self._data.get(id(instance)):
            return value_tuple[1]

    def __set__(self, instance, value):
        self._data[id(instance)] = (weakref.ref(
            instance, self._remove_object), value)

    def _remove_object(self, weak_ref):
        print(f'_remove_object called {weak_ref=}')
        found_key = None
        for key, (weak_ref_inst, _) in self._data.items():
            if weak_ref_inst is weak_ref:
                found_key = key
                break
        if found_key is not None:
            del self._data[found_key]


class MyClass:
    x = Desc()
    y = Desc()
    z = Desc()


if __name__ == '__main__':
    my_inst1 = MyClass()
    my_inst1.x = 1
    my_inst1.y = 2
    my_inst1.z = 3

    my_inst2 = MyClass()
    my_inst2.x = 11
    my_inst2.y = 22
    my_inst2.z = 33

    # {2462396503248: (<weakref at 0x0000023D5244A1B0; to 'MyClass' at 0x0000023D5244D4D0>, 1),
    #  2462396503504: (<weakref at 0x0000023D5244A250; to 'MyClass' at 0x0000023D5244D5D0>, 11)}
    print(MyClass.x._data)
    del my_inst1  # _remove_object called three times
```
如果觀察`MyClass.x._data`，可以看出其儲存了`my_inst1`及`my_inst2`的`weak reference`。當我們`del my_inst1`時，`self._remove_object`會被呼叫三遍，分別刪除`my_inst1`中的`x`、`y`及`z`三個`desc_instance`。

### 使用限制與缺點
`方法9`幾乎可以適用於任何場景。但與`方法8`一樣，當`MyClass`有使用`slots`時，記得要將`__weakref__`加入`__slots__`中。

## 當日筆記
* `方法5`和`方法6`非常像，只是`方法6`更為方便。
    * 因為`__set_name__`是Python3.6新加的功能，所以當要維護一些舊版本程式的時候，才比較有機會遇到`方法5`。
    * 當做一些prototype或side project時，我們可以使用`方法6`，因為可以確定`_name`是沒有被使用且可以使用`instance.__dict__`，但還是需謹慎使用。
* `方法7`和`方法8`是我們最常使用的方法：
    * 當`instance.__dict__`是可用的，我們會建議使用`方法7`。
    * 當`instance.__dict__`是不可用的且`instance`是`hashable`時，我們建議使用`方法8`。
* `方法9`是一個考慮周詳的方法，不過除非真的遇到這麼刁鑽的情況，使用`方法7`或`方法8`會來得更直觀簡單。
    * 當`instance.__dict__`是不可用的且`instance`不是`hashable`時，我們會建議使用`方法9`。
* 當`class`使用`slots`，且我們又使用如`方法8`或`方法9`的`weakref`方法時，記得將`__weakref__`加入`__slots__`中，否則將無法產生`weakref`。

## Code
[本日程式碼傳送門](https://github.com/jrycw/py10wings/tree/master/src/04_descriptor/day12_desc_design2)。