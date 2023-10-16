## 四翼大綱
一般我們從`instance`取得`attribute`或`function`時，會先由`instance.__dict__`找起，如果沒找到會再往上，順著生成`instance`的`class`的`mro`順序繼續找。`descriptor`是一種可以改變這種機制的有趣功能。雖然`descriptor`大部份應用會著重在由`instance`呼叫，這也會是我們接下來分享的重點，但是當其由`class`或是`super`呼叫時，各自有其細節要注意（`註1`）。

`descriptor`分為`non-data descriptor`及`data descriptor`。`non-data descriptor`為一有實作`__get__`的`class`，而`data descriptor`為一有實作`__get__`加上`__set__`或是`__delete__`兩種其一的`class`。

為方便稱呼，我將以`desc_instance`來稱呼由`descriptor` `class`生成的`instance`。

* [[Day10]](https://ithelp.ithome.com.tw/articles/10317762)介紹`non-data descriptor`與`data descriptor`。
* [[Day11]](https://ithelp.ithome.com.tw/articles/10317763)分享可能具有潛在問題的`descriptor`實作方法。
* [[Day12]](https://ithelp.ithome.com.tw/articles/10317764)分享比較通用的`descriptor`實作方法。
* [[Day13]](https://ithelp.ithome.com.tw/articles/10317765)比較`property` 與`Descriptor`。

## non-data descriptor
當我們想由`instance`取得`attribute`或`function`時，如果遇到`non-data descriptor`，會先確認該`attribute`或`function`是否存在於`instance.__dict__`中，如果有的話會優先使用，如果沒有的話才會使用`non-data descriptor`的`__get__`。

`__get__`的`signature`如下：
```python=
__get__(self, instance, owner_cls)
```
* `self`是實作有`__get__`的`non-data descriptor` `class`所生成的`instance`，我們稱作`desc_instance`。
* `instance`是`desc_instance`所在的`class`所生成的`instance`。
* `owner_cls`是生成`instance`的`class`。

乍看可能有點抽象，我們試著從`# 01`的例子中來說明。其中：
* `self`就是`MyClass`中的`non_data_desc`。
* `instance`就是`my_inst`。
* `owner_cls`就是`MyClass`。

```python=
# 01
class NonDataDescriptor:
    def __get__(self, instance, owner_cls):
        print('NonDataDescriptor __get__ called')


class MyClass:
    non_data_desc = NonDataDescriptor()


if __name__ == '__main__':
    my_inst = MyClass()
    print(f'{my_inst.__dict__=}')  # {}
    print(f'{my_inst.non_data_desc=}')  # None
    my_inst.non_data_desc = 10  # shadow
    print(f'{my_inst.non_data_desc=}')  # 10
    print(f'{my_inst.__dict__=}')  # {'non_data_desc': 10}
    print(f'{my_inst.non_data_desc=}')  # 10
```
```
my_inst.__dict__={}
NonDataDescriptor __get__ called
my_inst.non_data_desc=None
my_inst.non_data_desc=10
my_inst.__dict__={'non_data_desc': 10}
my_inst.non_data_desc=10
```
* 我們首先可以看看，`my_inst`剛由`MyClass`生成時，`my_inst.__dict__`為一個空的`dict`。
* 接下來我們使用`my_inst.non_data_desc`來取值，由於`my_inst.__dict__`找不到`non_data_desc`，所以會繼續使用`non_data_desc.__get__`來取值。而我們在`__get__`中只有印出參數，所以回傳值為`None`。
* 再來，我們使用`my_inst.non_data_desc=10`來賦值，這相當於在`my_inst.__dict__`中添加`non_data_desc`為10。這可以由再次觀察`my_inst.__dict__`來驗證。
* 此時我們如果再使用`my_inst.non_data_desc`來取值，因為`my_inst.__dict__`中已經有`non_data_desc`，所以會回傳10，而不會呼叫`non_data_desc.__get__`。


## data descriptor

當我們由`instance`存取`attribute`或`function`時，如果遇到`data descriptor`，會使用其實作的`__get__`及`__set__`(相當於`shadow` `instance.__dict__`)。

`__set__`的`signature`如下:
```python=
__set__(self, instance, value)
```
* `self`是實作有`__get__`及`__set__`的`data descriptor` `class`所生成的`instance`，即`desc_instance`本身。
* `instance`是`desc_instance`所在的`class`所生成的`instance`。
* `value`是所傳入想指定的值。

從`# 02`的例子中來說明。其中：
* `self`就是`MyClass`中的`data_desc`。
* `instance`就是`my_inst`。
* `value`就是`20`。

```python=
# 02
class DataDescriptor:
    def __get__(self, instance, owner_cls):
        print('DataDescriptor __get__ called')

    def __set__(self, instance, value):
        print(f'DataDescriptor __set__ called, {value=}')


class MyClass:
    data_desc = DataDescriptor()


if __name__ == '__main__':
    my_inst = MyClass()
    print(f'{my_inst.__dict__=}')  # {}
    my_inst.__dict__['data_desc'] = 10
    print(f'{my_inst.data_desc=}')  # None
    my_inst.data_desc = 20  # always use data_desc.__set__
    print(f'{my_inst.data_desc=}')  # None
    print(f'{my_inst.__dict__=}')  # {}
```
```
my_inst.__dict__={}
DataDescriptor __get__ called
my_inst.data_desc=None
DataDescriptor __set__ called, value=20
DataDescriptor __get__ called
my_inst.data_desc=None
my_inst.__dict__={'data_desc': 10}
```
* 我們一樣先確認`my_inst`剛由`MyClass`生成時，`my_inst.__dict__`為一個空的`dict`。
* 接著我們直接於`my_inst.__dict__`中手動插入`data_desc`為`10`（`註2`）。
* 接下來我們使用`my_inst.data_desc`來取值，由於`data_desc`會`shadow` `instance.__dict__`，所以將會呼叫`data_desc.__get__`。而我們在`__get__`中只有印出參數，所以回傳值為`None`。
* 再來，我們使用`my_inst.data_desc=20`來賦值，這會呼叫`data_desc.__set__`來進行賦值(但`__set__`目前僅呼叫一次`print`，並未實際賦值)。
* 最後，我們使用`my_inst.data_desc`來取值，此語法仍會呼叫`data_desc.__get__`，並回傳`None`。此時如果再次驗證`my_inst.__dict__`，會發現其中只有我們剛剛手動插入的`data_desc`，其值依然為`10`。

## 當日筆記
* `non-data descriptor` `class`生成的`desc_instance`**可能**會被`instance.__dict__` `shadow` 。
* `data descriptor` `class`生成的`desc_instance`**必定**會`shadow` `instacne.__dict__` 。

## 備註
註1：[Descriptor HowTo Guide](https://docs.python.org/3/howto/descriptor.html#overview-of-descriptor-invocation)。

註2：這邊我們必須使用這樣的語法，而不能使用`my_inst.data_desc = 10`，因為這樣會呼叫`data_desc.__set__`。


## 參考資料
`Descriptor`相關內容，大部份整理自[python-deepdive-Part 4-Section 08-Descriptors](https://github.com/fbaptiste/python-deepdive/tree/main/Part%204/Section%2008%20-%20Descriptors)、`Descriptor HowTo Guide`及`Python Morsels`練習題。


## Code
[本日程式碼傳送門](https://github.com/jrycw/py10wings/tree/master/src/04_descriptor/day10_nondata_vs_data_desc)。