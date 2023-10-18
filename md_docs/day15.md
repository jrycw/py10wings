# [Day15] 五翼 - Metaclasses : Class Creation
今天我們分享`class`是如何生成的，其實關鍵都在`type`這個`built-in`。

## `type`
[`type`](https://docs.python.org/3/library/functions.html#type)有兩種常用的使用情況：
1. 接受一個參數時，會回傳該參數的`type`。
2. 接受三個參數時，會回傳一個`class`，是一種動態生成`class`的方式。

`type`的`signature`如下：
```python=
type(cls_name, cls_bases, cls_dict)
```
* `cls_name`為想建立`class`的名字。
* `cls_bases`為新建立`class`的`MRO`上所有`class`，為一`tuple`。如果給予一個空的`tuple`，Python會自動將`object`加進去，即`(object, )`。
* `cls_dict`含有想建立`class`的所有資訊。

## 利用`type`建立`class`
```python=
# 01
class MyClass:
    def __init__(self, x):
        self.x = x
```
`# 01`是一個基本的`class`，我們可以將其拆為幾個部份，分別對應利用`type`建立`class`的過程：
* `class`是能夠建立`class`這種型態的關鍵字，在這裡我們想用`type`取代。
* `cls_name`為`'MyClass'`。
* `MyClass`為繼承`object`而來，即`cls_bases`為`(object, )`或以`空tuple`代替。
* `MyClass`內含有`function`或`attribute`的部份為`cls_body`。其實是一堆字串，我們需要一個方法來轉化這些字串，將轉換後的狀態記錄於`cls_dict`，使其能為`type`所用，而內建的[`exec`](https://docs.python.org/3/library/functions.html#exec)正好可以派上用場。

`# 02`模擬利用`type`建立`class`。
```python=
# 02
cls_dict = {}
cls_body = '''
def __init__(self, x):
    self.x = x
'''
exec(cls_body, globals(), cls_dict)  # populating cls_body into clas_dict
cls_name = 'MyClass'
cls_bases = ()
MyClass = type(cls_name, cls_bases, cls_dict)
```
## 利用`MyType`建立`class`
既然`type`是一種`class`，表示我們可以繼承`type`建立一個新的`MyType`。這麼一來，我們就可以overwrite `type.__new__`，在建立新`class`的前後動點手腳，最後再用類似前面`type`建立`class`的語法，使用`MyType`來建立`class`。
```python=
# 03
class MyType(type):
    def __new__(mcls, cls_name, _cls_bases, cls_dict):
        cls = super().__new__(mcls, cls_name, _cls_bases, cls_dict)
        return cls
    
... # 中間過程如# 02
MyClass = MyType(cls_name, cls_bases, cls_dict)
print(type(MyClass))  # <class '__main__.MyType'>
```
## 利用`class關鍵字`搭配`MyType`作為`metaclass`
可以看出使用`class`關鍵字來建立`class`，比使用`MyType`來的簡潔方便。但使用`MyType`的好處，是可以在建立`class`時動點手腳。那麼有沒有一種方法是既可以使用`class 關鍵字`來建立`class`，又同時具備我們在`MyType`中所做的操作呢？其實有的，而且我們一直隱性在用。

`# 04`中的`MyClass1`、`MyClass2`及`MyClass3`是等義的。**`class`是繼承`object`，並由`type`所生成。**
```python=
# 04
class MyClass1:
    def __init__(self, x):
        self.x = x


class MyClass2(object):
    def __init__(self, x):
        self.x = x


class MyClass3(object, metaclass=type):
    def __init__(self, x):
        self.x = x
```

所以我們只要將`metaclass`換為`MyType`，就可以繼續使用方便的`class 關鍵字`來建立`class`並同時具備於`MyType`中的操作。
```python=
# 04
...

class MyType(type):
    def __new__(mcls, cls_name, cls_bases, cls_dict):
        cls = super().__new__(mcls, cls_name, cls_bases, cls_dict)
        return cls


class MyClass(object, metaclass=MyType):
    def __init__(self, x):
        self.x = x
```
## `__prepare__`
本日內容至此，不知道您有沒有疑惑過下面這個問題。

當我們利用`MyType`來建立`class`，其`cls_dict`是我們給予的。但是當利用`class關鍵字`搭配`MyType`作為`metaclass`這種建立`class`的方式時，其中的`cls_dict`是哪裡來的呢？

其實此`cls_dict`會由`__prepare__`提供。如果`help(type)`，可以看出`__prepare__`為`class method`。
```
 |  Class methods defined here:
 |
 |  __prepare__(...)
 |      __prepare__() -> dict
 |      used to create the namespace for the class statement
```
一般來說，`__prepare__`會返回`dict`(但事實上可以返回一個`mapping`)，接著傳遞給`__new__`作為其`cls_dict`參數（`註1`）。然後我們可於`__new__`中對`cls_dict`進行一些操作。最後當我們使用`cls = super().__new__(mcls, cls_name, cls_bases, cls_dict)`時，會將`cls_dict`中的東西複製到一個新的`dict`中（`註2`）。

```python=
# 05
class MyType(type):
    @classmethod
    def __prepare__(cls, cls_name, cls_bases, **kwargs):
        print('MyType __prepare__ called')
        cls_dict = {}
        print(f'{id(cls_dict)=}')
        return cls_dict

    def __new__(mcls, cls_name, cls_bases, cls_dict):
        print('MyType __new__ called')
        print(f'{id(cls_dict)=}')
        cls = super().__new__(mcls, cls_name, cls_bases, cls_dict)
        return cls


class MyClass(metaclass=MyType):
    pass
```
```
MyType __prepare__ called
id(cls_dict)=2079093125440
MyType __new__ called
id(cls_dict)=2079093125440
```
由`# 05`中我們可以看出，`__prepare__`先於`__new__`被呼叫，且可以確認`__prepare__`中返回的`cls_dict`與`__new__`中的`cls_dict`是同一個`obj`。

Python3.7之前，一個有趣的運用是回傳一個`collections.OrderedDict`，來保存`key-value`的插入順序。但是新版本的`dict`已經是有序了，所以除非要維護舊版本的`code`，`__prepare__`漸漸失去了它的應用價值。有興趣深研的朋友可以參考[Python參考文件](https://docs.python.org/3/reference/datamodel.html?highlight=__call__#preparing-the-class-namespace)及[PEP 3115](https://peps.python.org/pep-3115/)。


## 備註
註1：於`__prepare__`傳到`__new__`的過程中，Python會幫我們加上一些`attribute`，如`__qualname__`等在此`dict`中。

註2：`cls_dict`並非新生成`cls`的`__dict__`。事實上`cls.__dict__`也僅為一`mappingproxy`。


## Code
[本日程式碼傳送門](https://github.com/jrycw/py10wings/tree/master/src/05_metaclasses/day15_class)。