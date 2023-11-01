# [Day29] 末翼 - Term Projects：Project Postman - 研究如何傳遞decorator factory之參數

## Postman源起
會想要研究這個小project，是因為在實作`project ECC`時，想要動態傳遞`ttl`。原先以為不太難，很快可以搞定，可是在玩了一陣子之後發現，當中有不少有趣的地方，所以想要有系統地做成筆記。

## Postman目標
`postman`是一個`decorator factory`，其接受一個`item`作為參數。`wrapper`內有一個`print`來幫忙確認傳進來的`item`值。
```python=
# postman.py
from functools import wraps


def postman(item):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            print(f'{item=} is received')
            return fn(*args, **kwargs)
        return wrapper
    return decorator
```
我們的目標是研究，有幾種方法可以動態傳遞`item`給`postman`，並裝飾(更精準的說法應該是`apply`)於`# 00`中`Class`的`func`上。

```python=
# 00
from postman import postman


class Class:

    def func(self):
        ...
```

理論上，`Class`的`func`應該是`non-data descriptor instance`，但是為方便描述，我們將稱呼其為`non-data descriptor`。


## 方法1：`instance.__dict__`
* 由於`func`為`non-data descriptor`，其由`instance`存取時，會返回由`types.MethodType`生成的`bound method`，所以`__init__`中一開始的`print(type(self.func))`為`method`。
* `postman(item)`會返回帶有`item`資訊的`decorator` `function`。所以`postman(item)(self.func)`相當於`decorator(self.func)`，會返回一個帶有`item`資訊的`wrapper` `function`。
* 由於`func`為`non-data descriptor`，其沒有`__set__`，所以`self.func = postman(item)(self.func)`相當於將帶有`item`資訊的`wrapper` `function`存於`inst.__dict__`中。此時觀察`print(type(self.func))`可以發現其已經變為`function`。
* 當我們呼叫`inst.func`時，相當於呼叫`wrapper`。其會呼叫`self.func`這個`bound method`後回傳。由於`self.func`是`bound method`，`self`會自己傳遞，所以`inst.func`，使用起來就像是一般的`instance method`。
* 最後假使將`func`由`inst.__dict__`中移除，我們還是可以使用`inst.func()`的語法來呼叫原來的`func`。

```python=
# 01
from postman import postman


class Class:
    def __init__(self, item):
        print(type(self.func))  # method
        self.func = postman(item)(self.func)
        print(type(self.func))  # function

    def func(self):
        ...


if __name__ == '__main__':
    inst = Class('xmas_card')
    inst.func()   # item='xmas_card' is received
    print(vars(inst))  # {'func': <function Class.func at 0x0000023BF70C6840>}
    del vars(inst)['func']
    inst.func()  # nothing shown on the screen
```

雖然`方法1`只有短短幾行，但中間發生了很多事情。我們認為這是個`hacky`的方法，`production code`可能不適合這麼寫。

## 方法2：`__new__`
`方法2`與`方法1`類似，只是我們改在`__new__`來做。
```python=
# 02
from postman import postman


class Class:
    def __new__(cls, item):
        inst = super().__new__(cls)
        inst.func = postman(item)(inst.func)
        return inst

    def func(self):
        ...


if __name__ == '__main__':
    inst = Class('xmas_card')
    inst.func()   # item='xmas_card' is received
```


## 方法3：`__new__`
`方法3`於生成`instance`前，先使用了`cls.func = postman(item)(cls.func)`後，再生成`instance`。

這麼做有個大問題，而且如果只利用`Class`生成一個`instance`的話，或許還觀察不出來。由於`__new__`是「每次」`Class`需要生成`instance`的時候，都會被呼叫一次。所以相當於每次生成`instance`，都會做一次`cls.func = postman(item)(cls.func)`。

`# 03`中我們只呼叫了一次`inst.func`，卻看到三個訊息被印出。因為 `Class('xmas_card')`、` Class('mail')`及`Class('package')`分別於`__new__`中都`mutate`了一次`func`。

```python=
# 03
from postman import postman


class Class:
    def __new__(cls, item):
        cls.func = postman(item)(cls.func)
        inst = super().__new__(cls)
        return inst

    def func(self):
        ...


if __name__ == '__main__':
    Class('xmas_card'), Class('mail')
    inst = Class('package')
    inst.func()
    # item='package' is received
    # item='mail' is received
    # item='xmas_card' is received
```

## 方法4：decorator(1)
`方法4`我們寫了一個名為`dec`的`decorator`，來裝飾在`Class`上。
* `dec`接受一個`item`參數後，返回一個`wrapper` `function`。
* `wrapper`接收一個`cls`參數，我們使用`vars(cls).get(name)`看看能不能從`cls.__dict__`中取到`func`。如果有取到的話，再進一步判斷其是否為`callable`。如果是的話，使用`setattr`重新設定`cls.name`為`postman(item)(obj))`。

由於我們`mutate`了`cls`，所以不管是在`mutate`前或後生成的`instance`都將會受影響。`mutate`的語法可以直接使用`dec('xmas_card')(Class)`。不過如果想寫成`Class = dec('xmas_card')(Class)`或是於`Class`上加上`@dec('xmas_card')`也是可以的。

```python=
# 04
from postman import postman


def dec(item):
    def wrapper(cls):
        name = 'func'
        if obj := vars(cls).get(name):
            if callable(obj):
                setattr(cls, name, postman(item)(obj))
        return cls
    return wrapper


class Class:
    def func(self):
        ...


if __name__ == '__main__':
    inst = Class()
    dec('xmas_card')(Class)
    inst2 = Class()
    inst2.func()  # item='xmas_card' is received
    inst.func()   # item='xmas_card' is received
```
由於我們是針對`vars(cls)`來進行搜尋，所以如`# 04a`中`func`定義於`ParentClass`而非`Class`的情況，此方法並不適用。

```python=
# 04a
...

class ParentClass:
    def func(self):
        ...


class Class(ParentClass):
    pass


if __name__ == '__main__':
    inst = Class()
    dec('xmas_card')(Class) 
    inst.func()   # nothing shown on the screen
```

## 方法5：decorator(2)
`方法5`與`方法4`類似，但我們使用`getattr`來尋找`cls.name`。

```python=
# 05
from postman import postman


def dec(item):
    def wrapper(cls):
        name = 'func'
        if obj := getattr(cls, name, None):
            if callable(obj):
                setattr(cls, name, postman(item)(obj))
        return cls
    return wrapper


class Class:
    def func(self):
        ...


if __name__ == '__main__':
    inst = Class()
    dec('xmas_card')(Class)  # Class is mutated
    inst.func()  # item='xmas_card' is received
```
由於這是`class`級別的`lookup`(可以參考[[Day18]](https://ithelp.ithome.com.tw/articles/10317770))，所以如`# 05a`中`func`定義於`ParentClass`而非`Class`的情況，此方法也可適用。

```python=
# 05a
...

class ParentClass:
    def func(self):
        ...


class Class(ParentClass):
    pass


if __name__ == '__main__':
    inst = Class()
    dec('xmas_card')(Class)
    inst.func()  # item='xmas_card' is received
```

## 方法6：metaclass(1)
`方法6`使用了與`方法4`類似的邏輯，只是這次使用了`metaclass`而不是`decorator`。此時`item`需要於`Class`生成時，以`keyword-only argument`傳遞，並需要記得於`Meta.__new__`中加入`item`的`signature`，才能存取到`item`。

```python=
# 06
from postman import postman


class Meta(type):
    def __new__(mcls, cls_name, cls_bases, cls_dict, item):
        cls = super().__new__(mcls, cls_name, cls_bases, cls_dict)
        name = 'func'
        if obj := vars(cls).get(name):
            if callable(obj):
                setattr(cls, name, postman(item)(obj))
        return cls



item = 'xmas_card'


class Class(metaclass=Meta, item=item):
    def func(self):
        ...


if __name__ == '__main__':
    inst = Class()
    inst.func()  # item='xmas_card' is received
```

與`# 04a`一樣，`# 06a`這種繼承的情況也不適用。
```python=
# 06a
...

item = 'xmas_card'


class ParentClass:
    def func(self):
        ...


class Class(ParentClass, metaclass=Meta, item=item):
    ...


if __name__ == '__main__':
    inst = Class()
    inst.func()  # nothing shown on the screen
```

## 方法7：metaclass(2)
`方法7`與`方法6`類似，但我們使用`getattr`來尋找`cls.name`。

```python=
# 07
from postman import postman


class Meta(type):
    def __new__(mcls, cls_name, cls_bases, cls_dict, item):
        cls = super().__new__(mcls, cls_name, cls_bases, cls_dict)
        name = 'func'
        if obj := getattr(cls, name, None):
            if callable(obj):
                setattr(cls, name, postman(item)(obj))
        return cls


item = 'xmas_card'


class Class(metaclass=Meta, item=item):
    def func(self):
        ...


if __name__ == '__main__':
    inst = Class()
    inst.func()  # item='xmas_card' is received
```
與`# 05a`一樣，`# 07a`這種繼承的情況也適用。
```python=
# 07a
...

item = 'xmas_card'


class ParentClass:
    def func(self):
        ...


class Class(ParentClass, metaclass=Meta, item=item):
    ...


if __name__ == '__main__':
    inst = Class()
    inst.func()  # item='xmas_card' is received
```

## 方法8：another class(1)
`方法8`與`方法6`的`Meta`是一樣的，但我們另外建立了一個`send_item` `function`。
* `send_item`接收一個參數`item`，並返回一個`wrapper` `function`。
* `wrapper` `function`接收一個參數`cls`，並複製所有`cls`的資訊加上於`send_item`傳入的`item`作為`Meta`的參數，來生成一個全新的`class`返回。


```python=
# 08
from postman import postman


class Meta(type):
    def __new__(mcls, cls_name, cls_bases, cls_dict, item):
        cls = super().__new__(mcls, cls_name, cls_bases, cls_dict)
        name = 'func'
        if obj := vars(cls).get(name):
            if callable(obj):
                setattr(cls, name, postman(item)(obj))
        return cls


def send_item(item):
    def wrapper(cls):
        return Meta(cls.__name__, cls.__bases__, dict(vars(cls)), item=item)
    return wrapper


item = 'xmas_card'


@send_item(item)
class Class:
    def func(self):
        ...


if __name__ == '__main__':
    inst = Class()  # type(Class) => <class '__main__.Meta'>
    inst.func()  # item='xmas_card' is received
```
與`# 04a`與`#06a`一樣，`# 08a`這種繼承的情況也不適用。
```python=
# 08a
...

class ParentClass:
    def func(self):
        ...


@send_item(item)
class Class(ParentClass):
    ...


if __name__ == '__main__':
    inst = Class()
    inst.func()  # nothing shown on the screen
```

## 方法9：another class(2)
`方法9`與`方法8`類似，但我們使用`getattr`來尋找`cls.name`。
```python=
# 09
from postman import postman


class Meta(type):
    def __new__(mcls, cls_name, cls_bases, cls_dict, item):
        cls = super().__new__(mcls, cls_name, cls_bases, cls_dict)
        name = 'func'
        if obj := getattr(cls, name, None):
            if callable(obj):
                setattr(cls, name, postman(item)(obj))
        return cls


def send_item(item):
    def wrapper(cls):
        return Meta(cls.__name__, cls.__bases__, dict(vars(cls)), item=item)
    return wrapper


item = 'xmas_card'


@send_item(item)
class Class:
    def func(self):
        ...


if __name__ == '__main__':
    inst = Class()
    inst.func()  # item='xmas_card' is received
```
與`# 05a`與`# 07a`一樣，`# 09a`這種繼承的情況也適用。
```python=
# 09a
...

class ParentClass:
    def func(self):
        ...


@send_item(item)
class Class(ParentClass):
    ...


if __name__ == '__main__':
    inst = Class()
    inst.func()  # item='xmas_card' is received
```

## 方法10：pure function(1)
`方法10`直接建立一個`function`，接收`cls`及`item`兩個參數後，直接於`function`中`mutate` `cls`，重新將`cls.name`指定為`postman(item)(obj)`後，返回`cls`。
```python=
# 10
from postman import postman


def send_item(cls, item):
    name = 'func'
    if obj := vars(cls).get(name):
        if callable(obj):
            setattr(cls, name, postman(item)(obj))
    return cls


class Class:
    def func(self):
        ...


if __name__ == '__main__':
    send_item(Class, 'xmas_card')
    inst = Class()
    inst.func()   # item='xmas_card' is received
```
`# 10a`這種繼承的情況也不適用。
```python=
# 10a
...

item = 'xmas_card'


class ParentClass:
    def func(self):
        ...


class Class(ParentClass):
    ...


if __name__ == '__main__':
    send_item(Class, 'xmas_card')
    inst = Class()
    inst.func()   # nothing shown on the screen
```


## 方法11：pure function(2)
`方法11`與`方法10`類似，但我們使用`getattr`來尋找`cls.name`。
```python=
# 11
from postman import postman


def send_item(cls, item):
    name = 'func'
    if obj := getattr(cls, name, None):
        if callable(obj):
            setattr(cls, name, postman(item)(obj))
    return cls


class Class:
    def func(self):
        ...


if __name__ == '__main__':
    send_item(Class, 'xmas_card')
    inst = Class()
    inst.func()   # item='xmas_card' is received
```

`# 11a`這種繼承的情況也適用。
```python=
# 11a
...

item = 'xmas_card'


class ParentClass:
    def func(self):
        ...


class Class(ParentClass):
    ...


if __name__ == '__main__':
    send_item(Class, 'xmas_card')
    inst = Class()
    inst.func()   # item='xmas_card' is received
```
## 方法12：class body
`方法12`為將`item`設定於`class body`中作為`class variable`。
```python=
# 12
from postman import postman


class Class:
    item = 'xmas_card'

    @postman(item)
    def func(self):
        ...


if __name__ == '__main__':
    inst = Class()
    inst.func()  # item='xmas_card' reveived
```

## 方法13：global scope
`方法13`為將`item`設定於`global scope`中。
```python=
# 13
from postman import postman

item = 'xmas_card'


class Class:

    @postman(item)
    def func(self):
        ...


if __name__ == '__main__':
    inst = Class()
    inst.func()  # item='xmas_card' reveived
```

## 後記
* 這個project的目標，是希望能夠動態傳入參數至已建立的`function`中。如果是要建立一個尚不存在的`function`，經裝飾後再設為`cls`或`self`的`attribute`的話，可能會需要`types.MethodType`的幫忙。
* 這個project我們假設`function`的`name`(`func`)是已知的，其實我們可以考慮將需要裝飾的`name(s)`作為一個`container`收集起來，也當作參數與`item`一起傳遞到`decorator`或`Meta`內，再使用迴圈處理。

## Code
[本日程式碼傳送門](https://github.com/jrycw/py10wings/tree/master/src/10_term_projects/day29_project_postman)。