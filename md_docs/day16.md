# [Day16] 五翼 - Metaclasses：`__call__``
今天我們來聊聊`__call__`。希望透過今天的內容，我們更清楚` my_inst(...)`、`MyClass(...)`及`MyType(...)`或`class MyClass(metaclass=MyType)`等語法背後的意義。

我們先記錄以下這段關於`type.__call__`的論述，稍後再輔以範例說明。

>`type`預設實作有`__call__`，當其被`call`時，會呼叫所傳入`type instance`的`__new__`。如果其返回的是該`type instance`的`instance`時(稱作`inst`)，會再幫忙呼叫`type instance`的`__init__`，最後回傳`inst`。`type instance`可能為`class`或其它繼承`type`的`metaclass`或是`type`本身。


## my_inst(...)
當生成`instance`的`class`有實作`__call__`時，該`instance`為`callable`。

`# 01`中，`my_inst`因為`MyClass`有實作`__call__`，所以是`callable`。
```python=
# 01
class MyClass:
    def __call__(self):
        print('MyClass __call__ called because of `my_inst()`')


if __name__ == '__main__':
    my_inst = MyClass()
    my_inst()  # my_inst is callable
```
```
MyClass __call__ called because of `my_inst()`
```



## MyClass(...)
當生成`class`的`metaclass`有實作`__call__`時，該`class`為`callable`。`# 02`中，`MyClass`的`metaclass`(`MyType`)有實作`__call__`，所以`MyClass`為`callable`。

當`MyClass`被呼叫時，相當於呼叫`MyType.__call__`，而其將此呼叫`delegate`給`super()__call__`。`super()__call__`相當於`super(MyType, cls)__call__`，也就是說會將`cls`（即`MyClass`）傳入`type.__call__`（`MyClass`是`type`的`instance`）。結合開頭對`type.__call__`的描述，我們可以了解`type.__call__`會幫忙呼叫`MyClass.__new__`。由於`MyClass.__new__`回傳了一個`MyClass`的`instance`，所以`MyClass.__init__`也會被呼叫。

```Python=
# 02
class MyType(type):
    def __call__(cls, *args, **kwargs):
        print('MyType __call__ called because of `MyClass()`')
        instance = super().__call__(*args, **kwargs)
        return instance


class MyClass(metaclass=MyType):
    def __new__(cls):
        print('MyClass __new__ called')
        instance = super().__new__(cls)
        return instance

    def __init__(self):
        print('MyClass __init__ called')

    def __call__(self):
        print('MyClass __call__ called because of `my_inst()`')


if __name__ == '__main__':
    my_inst = MyClass()  # MyClass is callable as well
    my_inst()   # my_inst is callable
```
```
MyType __call__ called because of `MyClass()`
MyClass __new__ called
MyClass __init__ called
MyClass __call__ called because of `my_inst()`
```


### MyType(...) 
當生成`metaclass`的`metaclass`有實作`__call__`時，該`metaclass`（第一個`metaclass`）為`callable`。`# 03`中，`MyType`的`metaclass`（`type`）有實作`__call__`，所以`MyType`為`callable`（這就是為什麼我們可以寫出`MyType(...)`或`class MyClass(metaclass=MyType)`這類語法的原因）。

當`MyType`被呼叫時，相當於呼叫`type.__call__`，此時`MyType`會被傳入`type.__call__`（`MyType`是`type`的`instance`）。`type.__call__`會幫忙呼叫`MyType.__new__`。由於`MyType.__new__`回傳了一個`MyType`的`instance`（即`class`），所以`MyType.__init__`也會被呼叫。

此處因為很容易出錯，所以需要再加強說明。`MyType.__new__`及`MyType.__init__`之所以被`call`，並不是因為實作有`MyType.__call__`，而是因為`type`實作有`__call__`。`MyType.__call__`是為了生成其`instance`而準備的（例如`MyClass`），與`MyType`是否為`callable`沒有關係。

```python=
# 03
class MyType(type):
    def __new__(mcls, cls_name, cls_bases, cls_dict, **kwargs):
        print('MyType __new__ called')
        cls = super().__new__(mcls, cls_name, cls_bases, cls_dict)
        return cls

    def __init__(cls, cls_name, cls_bases, cls_dict, **kwargs):
        print('MyType __init__ called')

    def __call__(cls, *args, **kwargs):
        print('MyType __call__ called because of `MyClass()`')
        instance = super().__call__(*args, **kwargs)
        return instance


class MyClass(metaclass=MyType):  # MyType is callable as well
    def __new__(cls):
        print('MyClass __new__ called')
        instance = super().__new__(cls)
        return instance

    def __init__(self):
        print('MyClass __init__ called')

    def __call__(self):
        print('MyClass __call__ called because of `my_inst()`')


if __name__ == '__main__':
    my_inst = MyClass()  # MyClass is callable as well
    my_inst()   # my_inst is callable
```
```
MyType __new__ called
MyType __init__ called
MyType __call__ called because of `MyClass()`
MyClass __new__ called
MyClass __init__ called
MyClass __call__ called because of `my_inst()`
```
### type(...)
`type`的`metaclass`還是`type`，而`type`實作有`__call__`，所以`type`為`callable`。

當`type`被`call`時，相當於呼叫`type`的`metaclass`的`__call__`也就是`type.__call__`，此時`type`會被傳入`type.__call__`（`type`是`type`的`instance`）。`type.__call__`會負責生成一個`type`的`instance`（即`class`）。

## 本日筆記
* 當一個`obj`是`callable`時，代表建立其的`class`實作有`__call__`。換句話說，`class`實作的`__call__`是為其`instance`作準備，而不是自己。當`class`本身也要是`callable`時，代表建立其的`metaclass`也要實作有`__call__`。

* 如果對上一點很難理解的話，您可以將`instance`、`class`、`MyType`等的生成過程，想成是不同層級的情況，幫助理解。
    * 當一個`instance`是`callable`時，代表建立其的`class`實作有`__call__`。換句話說，`class`實作的`__call__`是為其`instance`作準備，而不是自己。當`class`本身也要是`callable`時，代表建立其的`metaclass`也要實作有`__call__`。 
    * 當一個`class`是`callable`時，代表建立其的`metaclass`實作有`__call__`。換句話說，`metaclass`實作的`__call__`是為其`instance`（即`class`）作準備，而不是自己。當`metaclass`本身也要是`callable`時，代表建立其的`metaclass`（或是可以想成`meta-metaclass`）也要實作有`__call__`。 
    * ...

* 有時候，可能會對`__call__`到底會產生何種行為，會呼叫誰的`__new__`和`__init__`感到疑惑。此時關鍵是想清楚，究竟是誰在呼叫，是`my_inst(...)`、`MyClass(...)`、`MyType(...)`或`type(...)`中的哪一層。


## Code
[本日程式碼傳送門](https://github.com/jrycw/py10wings/tree/master/src/05_metaclasses/day16_dunder_call)。