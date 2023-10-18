# [Day17] 五翼 - Metaclasses : Metaclasses相關整理
今天我們來歸納整理一下`metaclass`相關的知識。

`# 01`為稍後會用到的程式碼，其內含有：
* 一個名為`MyClass`的`class`。
* 一個由`MyClass`生成，名為`my_inst`的`instance`。
```python=
# 01
class MyClass(object, metaclass=type):
    pass

my_inst = MyClass()
```
## 環環相扣的object與type
以下是我們能想到最精簡能解釋`object`、`type`、`class`、`instance`關係的解釋，或許您也會想參考[這篇stackoverflow的討論](https://stackoverflow.com/questions/50500298/isinstancetype-object-true-why)。

在Python，萬物皆是`object`，所以萬物都是繼承`object`而來(包含`object`自己)。所以
```python=
>>> isinstance(object, object)  # True
>>> issubclass(object, object)  # True
```

我們說`my_inst`是`MyClass`的`instance`。所以`type(my_inst)`是`MyClass`。

同理，藉由觀察`type(MyClass)`為`type`，可以得知`MyClass`是`type`的`instance`(`MyClass(metaclass=type)`是強烈暗示)。

那麼再往上推，藉由觀察`type(type)`為`type`，可以得知`type`也是`type`的`instance`。其實`type is type`也會是`True`。這就像一個`circular reference`。所以
```python=
>>> isinstance(type, type)  # True
>>> issubclass(type, type)  # True
```

而`MyClass`是繼承`object`而來(`MyClass(object)`是強烈暗示)，且`MyClass`既然是`type`的`instance`，那麼`object`必定也是`type`的`instance`。所以
```python=
>>> isinstance(object, type)  # True
```
再加上`type`的`circular reference`，所以
```python=
>>> issubclass(object, type)  # True
```

`type`也是繼承`object`而來，再加上`type`的`circular reference`，所以
```python=
>>> isinstance(type, object)  # True
>>> issubclass(type, object)  # True
```


## class creation
* 所有`class`都是繼承`object`而來，且預設`metaclass`為`type`。
* 當Python看到`class`關鍵字後，知道我們想生成一個`class`時，會先呼叫`type.__prepare__`，準備一個`mapping`，做為稍後傳給`type.__new__`的`cls_dict`，裡面會幫我們加上一些`attribute`(如`__qualname__`)。
* 生成一個`class`，相當於我們要呼叫`type`，`type`本身是`callable`，因為其`metaclass`(還是`type`)有實作`__call__`。`type.__call__`會先呼叫`type.__new__`，如果回傳的是`MyClass`的話，則會再呼叫`type.__init__`。至此`MyClass`生成完畢。

## instance creation
* 生成一個`instance`，相當於我們要呼叫`MyClass`，這會呼叫`MyClass`的`metaclass`的`__call__`，即`type.__call__`。`type.__call__`會呼叫`MyClass.__new__`，如果其回傳的是`MyClass`的`instance`，則會再呼叫`MyClass.__init__`。


## 實例說明 
`# 02`中，我們講解了`class`與`instance`的生成過程，並提供數個可以生成`class variable`及`instance variable`的方法。
```python=
# 02
class MyType(type):
    mcls_var_x = 'x'

    def __prepare__(cls, cls_bases, **kwargs):
        cls_dict = {'cls_var_a': 'a'}
        return cls_dict

    def __new__(mcls, cls_name, cls_bases, cls_dict, **kwargs):
        cls_dict['cls_var_c'] = 'c'
        cls = super().__new__(mcls, cls_name, cls_bases, cls_dict)
        cls.say_hello = lambda self: 'MyType works!'
        return cls

    def __init__(cls, cls_name, cls_bases, cls_dict, **kwargs):
        cls.cls_var_d = 'd'

    def __call__(cls, *args, **kwargs):
        instance = super().__call__(*args, **kwargs)
        instance.inst_var_c = 'c'
        return instance


class MyParentClass:
    cls_var_e = 'e'

    def good_morning(self):
        return 'Good morning!'


class MyClass(MyParentClass, metaclass=MyType):
    cls_var_b = 'b'

    def __new__(cls, b):
        instance = super().__new__(cls)
        instance.inst_var_a = 'a'
        return instance

    def __init__(self, b):
        self.inst_var_b = b


if __name__ == '__main__':
    my_inst = MyClass('b')
    cls_vars = {k: v
                for k, v in vars(MyClass).items()
                if k.startswith('cls_')}
    # {'cls_var_a': 'a', 'cls_var_b': 'b', 'cls_var_c': 'c', 'cls_var_d': 'd'}
    print(cls_vars)

    inst_vars = vars(my_inst)
    # {'inst_var_a': 'a', 'inst_var_b': 'b', 'inst_var_c': 'c'}
    print(inst_vars)

    # MyType.__new__
    print(my_inst.say_hello())  # MyType works!

    # MyParentClass
    print(my_inst.cls_var_e, MyClass.cls_var_e)  # e e
    print(my_inst.good_morning())  # Good morning!

    # MyType
    print(MyClass.mcls_var_x)  # x
    # print(my_inst.mcls_var_x)  # AttributeError

    # (<class '__main__.MyType'>, <class 'type'>, <class 'object'>)
    print(type(MyClass).__mro__)

    # (<class '__main__.MyClass'>, <class '__main__.MyParentClass'>, <class 'object'>)
    print(MyClass.__mro__)
```
### 生成MyClass
`MyClass`由`MyType`所生成。
* `MyType.__prepare__`會先生成一個`mapping`，我們此處直接生成一個`dict`，並於其中建立`cls_var_a`。
* `MyType`會呼叫`type.__call__`(不是`MyType.__call__`)，幫忙呼叫`MyType.__new__`(不是`type.__new__`，因為`MyType`呼叫`type.__call__`時，有將`MyType`的資訊傳給`type.__call__`)。
* 於`MyType.__new__`中，我們利用`super().__new__`(即`type.__new__`)來生成`MyClass`。此時的`cls_dict`中除了`cls_var_a`還有位於`MyClass`中的`cls_var_b`。我們可以選擇將想建立的`attribute`或`function`放入`cls_dict`中，或是於生成`MyClass`後再動態指定。此處我們演示將`cls_var_c`放入`cls_dict`並於生成`MyClass`後，再動態指定`say_hello` `function`。
* 由於`MyType.__new__`中返回的是`MyClass`，所以`type.__call__`會幫忙呼叫`MyType.__init__`。於`MyType.__init__`中我們加入`cls_var_d`。

### 生成my_inst
* 生成`my_inst`需要呼叫`MyClass`，所以會呼叫`MyType.__call__`。
* `MyType.__call__`將呼叫的工作delegate給`super().__call__`，所以實際上幫忙我們建立`instance`的是`type.__call__`。但此處我們將`MyClass`的資訊藉由`super().__call__`傳給`type.__call__`，所以Python會呼叫`MyClass.__new__`(非`type.__new__`)來生成`instance`。
* 於`MyClass.__new__`中我們加入`inst_var_a`。由於回傳的是`MyClass`的`instance`，所以`MyType.__call__`會幫忙呼叫`MyClass.__init__`。於`MyClass.__init__`中我們加入`inst_var_b`。
* 最後，我們於`MyType.__call__`回傳`instance`前加入`inst_var_c`。

### 存取其它attribute
上面我們示範了`cls_var_a`、`cls_var_b`、`cls_var_c`、`cls_var_d`、`inst_var_a`、`inst_var_b`、`inst_var_c`以及`say_hello` `function`是如何生成的。

接下來討論兩個有趣的情況。
####  MyParentClass
因為`MyClass`繼承`MyParentClass`，所以可以存取位於`MyParentClass`的`cls_var_e`及`good_morning` `function`。

#### MyType
如果使用`MyClass.mcls_var_x`可以取回`'x'`，但若使用`my_inst.mcls_var_x`會`raise AttributeError`。

不知道諸位對這個行為是否會感到疑惑呢？如果要了解Python整個`attribute lookup`，可能要閱讀六翼的文章。

簡單解釋的話是當於`instance.__dict__`找不到某`attribute`時，會往生成其的`class`及其`MRO`的`__dict__`中尋找。

> `type(MyClass).__mro__`為`(MyType, type, object)`

由於`MyClass`是`MyType`的`instance`，當於`MyClass.__dict__`找不到`mcls_var_x`時，會往`MyType.__dict__`尋找。由於`mcls_var_x`是`MyType`的`class variable`，所以返回其值`'x'`。

> `Myclass.__mro__`為`(MyClass, MyParentClass, object)`

至於`my_inst`是`MyClass`的`instance`，當於`myinst.__dict__`找不到`mcls_var_x`時，會往`MyClass.__dict__`尋找。由於找不到，於是再往上至`MyParentClass.__dict__`尋找。由於還是找不到，於是再往上至`object.__dict__`尋找。最後由於整個`MRO`中都找不到`mcls_var_x`，只能`raise AttributeError`給使用者。

## `__init_subclass__`
`__init_subclass__`是於Python3.6所添加的，其會於`type.__new__`生成`class`後才被[呼叫](https://docs.python.org/3/reference/datamodel.html#creating-the-class-object)。`type.__new__`會先收集有實作`__set_name__`的`attribute`，於`class`生成後呼叫這些`attribute`的`__set_name__`。接下來`__init_subclass__`會由`MRO`上最接近的parent class來呼叫。

`__init_subclass__`是一個`class method`，它給我們一個使用繼承來`mutate` `class`的選項。我們可以使用其添加`class`的`attribute`或`function`等等，一些以前必須要在`type.__new__`中的邏輯，可以轉移到這邊，而不需要自己客製`metaclass`。

## 小結
最後，每當迷失在`metaclass`的世界時，下面這段話總是能幫到我們，希望對您也有幫助。

**`instance`由`class`所生成，所以`instance`是`class`生成的`instance`。
`class`由`metaclass`所生成，所以`class`是`metaclass`生成的`instance`。**

將`class`視為一種`instance`，再回頭看`metaclass`時，會有一種撥雲見日的感覺。

## 參考資料
1. [Python Morsels - Everything is an object](https://www.pythonmorsels.com/everything-is-an-object/)。
2. [Real Python - metaclasses](https://realpython.com/python-metaclasses/)。
3. [Python 3:Deep Dive part4-155 - Classes, Metaclasses, and `__call__`](https://www.udemy.com/course/python-3-deep-dive-part-4/learn/lecture/16786068#overview)。

## Code
[本日程式碼傳送門](https://github.com/jrycw/py10wings/tree/master/src/05_metaclasses/day17_metaclasses)。