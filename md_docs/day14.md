# [Day14] 五翼 - Metaclasses：Instance Creation
## 五翼大綱
`metaclasses`可以說是Python最難掌握的範疇。如果是第一次接觸這些概念，很容易出現`我是誰？`，`我在幹麻？`，`我要去哪裡？`的徵狀。如果出現類似的情形，請不要驚慌，這是非常正常的XD

在日常應用中，直接使用`metaclasses`的機會不高，但了解`metaclasses`能讓我們由另一個視角，來欣賞Python的優雅。

下面引用Python大神，`Tim Peters`（`註1`），對於`metaclasses`的描述：
> “Metaclasses are deeper magic than 99% of users should ever worry about. If you wonder whether you need them, you don’t (the people who actually need them know with certainty that they need them, and don’t need an explanation about why).”
— Tim Peters

* [[Day14]](https://ithelp.ithome.com.tw/articles/10317766)分享`instance`的`initialize`及`instantiate`。
* [[Day15]](https://ithelp.ithome.com.tw/articles/10317767)分享`class`的生成過程。
* [[Day16]](https://ithelp.ithome.com.tw/articles/10317768)分享使用`__call__`的細節。
* [[Day17]](https://ithelp.ithome.com.tw/articles/10317769)整理`metaclasses`相關知識。

## initialize vs instantiate
Python的`class`是繼承`object`而來，所以
```python=
class MyClass:
    pass
```
是等義於
```python=
class MyClass(object):
    pass
```
如果`help(object)`，可以看到其內建有`__init__`(`instance method`)及`__new__`(`static method`)。
```
 |  __init__(self, /, *args, **kwargs)
 |      Initialize self.  See help(type(self)) for accurate signature.

 |  Static methods defined here:
 |
 |  __new__(*args, **kwargs) from builtins.type
 |      Create and return a new object.  See help(type) for accurate signature.
```
* `initialize`是指`instance`已經建立，而我們要進一步初始化，一般為呼叫`__init__`。

* `instantiate`則是指使用`__new__`建立`instance`。

## `__init__`
`# 01`中，建立了客製化的`__init__`（即overwrite了`object.__init__`），使得透過`MyClass`建立的`instance`於初始化時，可以指定`instance variable` `self.x`的值。
```python=
# 01
class MyClass:
    def __init__(self, x):
        self.x = x


if __name__ == '__main__':
    my_inst = MyClass(1)
    print(my_inst.__dict__)  # {'x': 1}
```
`__init__`是個`instance method`，而`instance method`的第一個參數，一般約定俗成地取名為`self`。既然`self`能夠被傳入`__init__`，代表`instance`本身是在`__init__`被呼叫前即已建立。

## `__new__`
事實上，`object.__new__`才是Python真正建立`instance`時所呼叫的。

`# 02`中，建立了客製化的`__new__`（即overwrite了`object.__new__`）。
* `__new__`的第一個參數為`cls`，在`# 02`中即為`MyClass`，至於其它參數則需要與`__init__`一致（如果有的話）。
* 在`__new__`中呼叫`super().__new__(cls)`來建立`instance`，在`# 02`中呼叫`super().__new__(cls)`相當於呼叫`object.__new__(cls)`，但習慣使用`super()`的寫法，可以幫助我們在繼承的時候，減少一些問題（`註2`）。
* 當`__new__`回傳一個`MyClass`的`instance`時（`註3`），會自動呼叫`__init__`，我們可以`id`來確認`__new__`中的`instance`就是傳入`__init__`中的`self`。

```python=
# 02
class MyClass:
    def __new__(cls, x):
        instance = super().__new__(cls)
        print(f'{id(instance)=}')
        return instance

    def __init__(self, x):
        print(f'{id(self)=}')
        self.x = x


if __name__ == '__main__':
    my_inst = MyClass(1)
    print(my_inst.__dict__)  # {'x': 1}
```
理論上，任何在`__init__`中能做的事，都能夠在`__new__`中完成。

`# 03`中，我們將`__init__`中指定的`instance variable` `self.x`搬到`__new__`中，如此則可免去建立`__init__`。
```python=
# 03
class MyClass:
    def __new__(cls, x):
        instance = super().__new__(cls)
        instance.x = x
        return instance


if __name__ == '__main__':
    my_inst = MyClass(1)
    print(my_inst.__dict__)  # {'x': 1}
```
如果對於理解`# 03`有困難的朋友，或許可以將`instance`想為`self`，改寫為`# 04`。
```python=
# 04
class MyClass:
    def __new__(cls, x):
        self = super().__new__(cls)
        self.x = x
        return self


if __name__ == '__main__':
    my_inst = MyClass(1)
    print(my_inst.__dict__)  # {'x': 1}
```
### 實例說明1
假設現在有個`SlowNewClass`，而其`__new__`有很多操作，需時良久（以`time.sleep(1)`表示）。
```python=
# 05
import time


class SlowNewClass:
    def __new__(cls,  **kwargs):
        time.sleep(1)
        return super().__new__(cls)

    def __init__(self, **kwargs):
        self.__dict__.update(**kwargs)
...
```
題目要求：
* 建立客製化的`class`，且必須繼承`SlowNewClass`。
* 客製化的`class`僅接受`**kwargs`參數，且`kwargs`內所有`value`必須滿足`value>=0`，否則`raise ValueError`。若`kwargs`中有`x`變數，需要將其從`kwargs`移出，進行某些操作（以`self.x = x+100`表示），再將剩下的`kwargs`利用`super().__init__`往上傳遞。

於`# 05`中，我們建立了`MyClass`與`MyClass2`，並利用`timer`來觀察`instance`的生成速度。
```python=
# 05
...
def timer(cls, **kwargs):
    try:
        start = time.perf_counter()
        my_inst = cls(**kwargs)
    except ValueError:
        pass
    finally:
        end = time.perf_counter()
        elapsed = end - start
        print(f'{elapsed=:.6f} secs for {cls}')

        
class MyClass(SlowNewClass):
    def __init__(self, **kwargs):
        if all(value >= 0 for value in kwargs.values()):
            if x := kwargs.pop('x', None):
                self.x = x+100
            super().__init__(**kwargs)
        else:
            raise ValueError


class MyClass2(SlowNewClass):
    def __new__(cls, **kwargs):
        if all(value >= 0 for value in kwargs.values()):
            return super().__new__(cls, **kwargs)
        raise ValueError

    def __init__(self, **kwargs):
        if x := kwargs.pop('x', None):
            self.x = x+100
        super().__init__(**kwargs)
        
        
if __name__ == '__main__':
    my_inst = MyClass(x=1, y=2)
    print(my_inst.__dict__)  # {'x': 101, 'y': 2}

    my_inst2 = MyClass2(x=1, y=2)
    print(my_inst2.__dict__)  # {'x': 101, 'y': 2}

    print('normal: ')
    timer(MyClass, x=1, y=2)  # 1.000700
    timer(MyClass2, x=1, y=2)  # 1.000952

    print('exceptions: ')
    timer(MyClass, x=-1, y=2)  # 1.000298
    timer(MyClass2, x=-1, y=2)  # 0.000011
```
* 一般來說，我們的實作會像`MyClass`，於`__init__`中進行操作。但是這有一個缺點是速度很慢，因為我們必須繼承`SlowNewClass`，透過其耗時的`__new__`來生成`instance`。換句話說，即使我們很快就判斷出需要`raise ValueError`，我們還是得等待`SlowNewClass.__new__`生成`instance`後才可操作。
* `MyClass2`同時實作`__new__`及`__init__`。這樣一來，我們可以於`__new__`呼叫`super()__new__`前，就先決定是否要`raise ValueError`，然後將後續需要呼叫`super().__init__`的工作放到`__init__`。
* 在正常情況下`MyClass`與`MyClass2`速度差不多，但是在有例外的情況下，`MyClass2`可以馬上`raise`。


### 實例說明2
由於`__new__`的第一個參數是`cls`，所以除了能指定`instance variable`外，也能對`MyClass`做一些手腳，例如插入一個`instance method` `hi`。

```python=
# 06
class MyClass:
    def __new__(cls, x: int):
        cls.hi = lambda self: 'hi'
        instance = super().__new__(cls)
        instance.x = x
        return instance


if __name__ == '__main__':
    my_inst = MyClass(1)
    print(my_inst.hi())  # hi
```
但是這麼寫有點「微妙」，因為這相當於在每次生成`instance`時，都會`mutate` `cls`一次，建立一個新的`instance method` `hi`。

### 實例說明3
`# 07`嘗試繼承`str`，並攔截給定字串，於其後加上`_123`。
```python=
# 07
class MyStr1(str):
    def __init__(self, s):
        super().__init__(s + '_123')


class MyStr2(str):
    def __new__(cls, s):
        return super().__new__(cls,  s + '_123')


if __name__ == '__main__':
    # my_str1 = MyStr1('abc') # TypeError
    my_str2 = MyStr2('abc')
    print(my_str2)  # 'abc_123'
```
* 於`MyStr1`中，`super().__init__`會`raise TypeError`。
* 於`MyStr2`中，`super().__new__`，則可以成功得到`abc_123`。

## 當日筆記
### 何時適合於`class`中實作`__new__`？
* 想要搶在`__init__`之前，於建立`instance`前後做一些操作時（`實例說明1`）。
* 於`__new__`中操控`cls`，暗指每次生成`instance`時，都會`mutate` `cls`，需謹慎考慮這是否為您想要的行為（`實例說明2`）。
* 當繼承以`C`實作的`built-in` `type`時。

## 備註
註1：`Tim Peters`也是著名`Zen of Python`的作者。什麼？您沒聽過嗎？那麼請打開Python的repl，輸入`import this`好好欣賞一下吧。

註2：如果不太熟悉`super()`的朋友，可以參考[這篇](https://rhettinger.wordpress.com/2011/05/26/super-considered-super/)由`Raymond Hettinger`所寫的介紹。

註3：如果`__new__`所回傳的並非`cls`的`instance`，則不會自動呼叫`__init__`。但儘管如此，我們可以手動呼叫`__init__`，所以可以寫出如`# 101`的`code`。
```Python=
# 101
from types import SimpleNamespace


class MyClass:
    def __new__(cls, x):
        return SimpleNamespace()

    def __init__(self, x):
        self.x = x

    def hi(self):
        return 'hi'


if __name__ == '__main__':
    my_inst = MyClass(1)  # __init__ not being called
    print(type(my_inst))  # <class 'types.SimpleNamespace'>
    MyClass.__init__(my_inst, 1)
    print(my_inst.__dict__)  # {'x': 1}
    print(MyClass.hi(my_inst))  # hi
```

## Code
[本日程式碼傳送門](https://github.com/jrycw/py10wings/tree/master/src/05_metaclasses/day14_instance)。
