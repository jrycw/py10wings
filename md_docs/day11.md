# [Day11] 四翼 - Descriptor：Descriptor存取設計(1)
`descriptor`就像是Python的倉庫管理員之一，在某些情況下(如[[Day10]](https://ithelp.ithome.com.tw/articles/10317762)所述)：
* 當其為`non-data descriptor`時，可以提供取的功能。
* 當其為`data descriptor`時，同時提供存取功能。

所以要從哪邊取值及要將值存去哪裡，是寫`descriptor`時，最須注意的地方。

一般來說，有兩個地方可以考慮，一個是`desc_instance`內，另一個是`instance.__dict__`，兩者都各有一些眉角。

接下來兩天，我們將練習數個`data descriptor`的寫法（`註1`）。今天會先分享一些有潛在問題的寫法，透過了解各方法的缺點或限制，漸漸學習反思。明天再分享一些通用的寫法。

以下將會用`desc_instance`來代稱`data descriptor instance`。

## 方法1
`方法1`試著將給定的值作為`instance variable`存在`desc_instance`內，即`# 01`中的`self._value`。
```python=
# 01
class Desc:
    def __get__(self, instance, owner_cls):
        return self._value

    def __set__(self, instance, value):
        self._value = value


class MyClass:
    x = Desc()


if __name__ == '__main__':
    my_inst1, my_inst2 = MyClass(), MyClass()

    # my_inst1
    my_inst1.x = 1
    print(f'{my_inst1.x=}')  # 1

    # my_inst2
    print(f'{my_inst2.x=}')  # 1
    my_inst2.x = 2
    print(f'{my_inst2.x=}')  # 2

    # my_inst1.x also changed
    print(f'{my_inst1.x=}')  # 2...not 1
```
```
my_inst1.x=1
my_inst2.x=1
my_inst2.x=2
my_inst1.x=2
```
* 於`MyClass`中建立名為`x`的`desc_instance`。
* 生成`my_inst1`及`my_inst2`兩個`instance`。此時若使用`my_inst1.x`或`my_inst2.x`將會呼叫`x.__get__`取值;若使用`my_inst1.x = 1`或`my_inst2.x = 2`將會呼叫`x.__set__`賦值。
* 透過`my_inst1.x = 1`將`1`指定給`x`內的`self._value`，並確認`my_inst1.x`的確為`1`。
* 接著觀察`my_inst2.x`，發現其已經有`1`這個值。這是因為`x`現在是一個`class variable`，所以`my_inst2.x`就是`my_inst1.x`。
* `my_inst2.x = 2`會將`2`指定給`x`內的`self._value`，也就是說`my_inst1.x`及`my_inst2.x`的回傳值都會是`2`。

### 使用限制與缺點
* 使用前需先透過類似`my_inst1.x = 1`的語法，指定值給`self._value`。
* 所有`MyClass`生成的`instance`都擁有能修改`x`的權力。

## 方法2
`方法2`試著將給定的值做為`instance variable`存在`instance`本身，即`# 02`中的`instance.hardcoded_name`。
```python=
# 02
class Desc:
    def __get__(self, instance, owner_cls):
        return getattr(instance, 'hardcoded_name', None)

    def __set__(self, instance, value):
        setattr(instance, 'hardcoded_name', value)


class MyClass:
    x = Desc()
    y = Desc()


if __name__ == '__main__':
    my_inst = MyClass()
    print(f'{my_inst.__dict__=}')  # {}

    my_inst.x = 1
    print(f'{my_inst.x=}')  # 1
    print(f'{my_inst.__dict__=}')  # {'hardcoded_name': 1}

    my_inst.x = 2
    print(f'{my_inst.x=}')  # 2
    print(f'{my_inst.y=}')  # 2
    print(f'{my_inst.__dict__=}')  # {'hardcoded_name': 2}
```
```
my_inst.__dict__={}
my_inst.x=1
my_inst.__dict__={'hardcoded_name': 1}
my_inst.x=2
my_inst.y=2
my_inst.__dict__={'hardcoded_name': 2}
```
* 於`MyClass`中建立`x`及`y`兩個`desc_instance`。
* 首先觀察`my_inst.__dict__`為一空`dict`。
* 透過`my_inst.x = 1`將`1`指定給`my_inst.hardcoded_name`，透過再次觀察`my_inst.__dict__`，可以確認`hardcoded_name`已在`instance.__dict__`中，且其值為`1`。
* 由於我們的`my_inst`只有準備一個`hardcoded_name`來作為存取`descriptor`的倉庫。所以當我們使用`my_inst.x = 2`時，其實相當於將`2`指定給`my_inst.hardcoded_name`，透過再次觀察`MyClass.__dict__`，可以確認`hardcoded_name`已在`instance.__dict__`中，且其值已變為`2`。

### 使用限制與缺點
* 於`MyClass`中，所有`Desc`生成的`desc_instance`將會共享一個固定的`instance variable`，即`instance.hardcoded_name`。


## 方法3
`方法3`嘗試於`descriptor`內建立一個`dict`，即`# 03`的`self._data`。我們以各`instance`本身為`self._data`的`key`，於`__set__`給定的`value`為`self._data`的`value`。
```python=
# 03
class Desc:
    def __init__(self):
        self._data = {}

    def __get__(self, instance, owner_cls):
        return self._data.get(instance)

    def __set__(self, instance, value):
        self._data[instance] = value


class MyClass:
    x = Desc()
    y = Desc()
```
如果進行和`方法1`及`方法2`類似的檢查，可以發現`方法3`也沒有類似的問題，但卻有一個非常大的缺點。

### 使用限制與缺點
* 由於`self._data`是將`instance`本身作為`key`，這代表即使我們手動使用`del`指令刪除了`instance`，也會是個假象，`instance`不會被`gc`(`garbage collect`)，因為至少還有一個`strong reference`存在。這是個嚴重的`memoey leak`，該被`gc`的`obj`卻還是存在，且有機會被存取。
* 即使不在意`memoey leak`，我們還必須確定`instance`是`hashalbe`，才能作為`self._data`的`key`。

## 方法4
`方法4`類似於`方法3`，但這次我們使用`id(instance)`為`self._data`的`key`。
```python=
# 04
class Desc:
    def __init__(self):
        self._data = {}

    def __get__(self, instance, owner_cls):
        return self._data.get(id(instance))

    def __set__(self, instance, value):
        self._data[id(instance)] = value

        
class MyClass:
    x = Desc()
    y = Desc()
```
如果進行和`方法1`及`方法2`類似的檢查，可以發現`方法4`也沒有類似的問題，且如果我們利用`del`來刪除`instance`時，該`instance`也真的會被`gc`。僅管如此，`方法4`還是有一些缺點。

### 使用限制與缺點
* 即使我們刪除了`instance`，其記憶體位置`id(instance)`，仍然以`int`型態存在`self._data`中。乍聽好像沒什麼關係，但是Python的記憶體位置是會重覆使用的。如果這個記憶體位置被其它`obj`使用了，我們的`descriptor`就隱含了這個不相關`obj`的資訊（雖然機率極低）。
* 其次即使記憶體位置沒有被重覆使用，但如果我們大量使用這類型的`descriptor`，也會造成很多無謂的記憶體浪費。

## 充電區
上面幾個方法讓我們對`descriptor`有了基本的認知。現在我們來充充電，講幾個實作`descriptor`時常會用到的觀念，為明天`descriptor`的通用寫法做好準備。

### 如何取得`desc_instance`
當我們應用`descriptor`時，有時需要取得`desc_instance`，一個常見的做法如下：
```python=
def __get__(self, instance, owner_cls):
    if instance is None:
        return self
    ...
```
在`__get__`一開始，先判斷`instance`是不是`None`。如果是`None`，代表我們是由`class`來取，直接返回`desc_instance`。也就是說當我們想取得`desc_instance`時，可以利用`MyClass.desc`的來取得。雖然我們大多數情況都是使用`instance`呼叫`desc_instance`，但當想觀察`desc_instance`內部狀態時，可以透過這個小技巧來達成。從明天的`方法5`開始，我們會於`__get__`中加上這一段程式碼。

### `__set_name__`
`__set_name__`的`signature`如下：
```python=
__set_name__(self, owner_cls, name)
```
`class`在定義時，會自動尋找有實作`__set_name__`的`attribute`，透過這個方法將他們在`class`的名字傳入`desc_instance`（`註2`）。舉例來說如果`Desc`實作有`__set_name__`，那麼`MyClass`中的`'x'`(`str`型態)於`MyClass`定義時，就會自動透過`x.__set_name__`傳入`desc_instance`。
```python=
class MyClass:
    x = Desc()
```
這個功能非常方便，可以讓我們在設計`descriptor`時，取得於`MyClass`中定義的名字。

### `__slots__`
當`class`實作有`__slots__`(一般定義為`tuple`)，未被列在其中的`attribute`，將無法由`instance`存取，這包括我們一直習以為常使用的`__dict__`。當然您也可以選擇使用`__slots__`然後手動將`__dict__`加進`__slots__`。

由`# 101`可以看出，當`MyClass`的`__slots__`設定為空的`tuple`時，我們無法使用`my_inst.__dict__`。但是在`MyClass2`中，我們手動加入`__dict__`後，就可以存取`my_inst2.__dict__`了。

__所以當我們說一個`instance.__dict__`可用時，代表其`class`未使用`slots`又或者有使用`slots`但是有將`__dict__`加進`__slots__`。__

```python=
# 101
class MyClass:
    __slots__ = ()


class MyClass2:
    __slots__ = ('__dict__',)


if __name__ == '__main__':
    my_inst = MyClass()
    print(f'{my_inst.__dict__=}')  # AttributeError

    my_inst2 = MyClass2()
    print(f'{my_inst2.__dict__=}')  # {}
```

或許您會想，應該不會有很多`Class`使用`slots`吧？但事實上，當程式需要大量由同個`class`生成的`instance`時，選擇使用`slots`，可以節省滿多的記憶體消耗。在一些與`database`相關的`ORM`應用或`iterator class`的實作上不算少見。

### `weak reference`
Python內建有`weakref module`，可以讓我們建立對某`obj`的`weak reference`。當該`obj`的`strong reference`為`0`時，此`weak reference`會收到通知，並且在有提供`callback function`時，呼叫這個`function`。而`weakref.WeakKeyDictionary`是一個可以自動幫我們建立及移除`weak reference`的方便容器。

想要能夠建立`weak reference`，其必須有`__weakref__` `attribute`。`__weakref__`是一個`data descriptor`，當我們對一個`obj`建立`weak reference`時，這個`weak reference object`其實就是存在`__weakref__`中。

當使用`slots`時，必須手動將`__weakref__`加進`__slots__`，否則將無法建立`weak reference`。
```python=
class MyClass:
    __slots__ = ('__weakref__',)
```

## 備註
註1：至於想實作`non-data descriptor`的朋友，相信可以由比較複雜的`data descriptor`中融會貫通而來。

註2：可以參考[Data Model](https://docs.python.org/3/reference/datamodel.html#creating-the-class-object)對這部份的說明。


## Code
[本日程式碼傳送門](https://github.com/jrycw/py10wings/tree/master/src/04_descriptor/day11_desc_design1)。