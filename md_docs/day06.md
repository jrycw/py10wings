# [Day06] 次翼 - Decorator : @class to func
今天我們分享`decorator class`裝飾於`function`上的情況。本日接下來內容，會以`decorator`來作為`decorator class`的簡稱。

另外，有些於`decorator function`提過的細節，將不特別重覆，直接入進本日重點。

## 核心概念
`decorator`的核心概念為接受一個`function`，從中做一些操作，最後返回一個`class`的`instance`。一般來說，返回的`instance`是個`callable`，會接收與原`function`相同的參數，並返回相同的結果，但卻能具有`decorator`額外賦予的功能。

## 基本型態
### 基本型態1
```python=
# 01
class dec:
    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)


@dec
def my_func(*args, **kwargs):
    pass
```
* 定義一個`decorator`，名為`dec`。其接收一個`function`，但卻返回一個`dec`生成的`instance`，稱作`dec_instance`。接收的`function`會被指定為`dec_instance`的`instance variable` `self.func`。
* 定義一個被`dec`裝飾的`function`，名為`my_func`，其可接受`*args`及`**kwargs`。


藉由`decorator`，`my_func`已經從原先的`my_func`變成`dec_instance`了。由於`__call__`（`註1`）與原先的`my_func`接收相同的參數（即`*args`及`**kwargs`），所以裝飾前後，`my_func`的呼叫方式是一致的。

當呼叫`my_func`時，實際上是在呼叫`dec_instance`。舉例來說，此時的`my_func(1, 2)`，相當於呼叫`dec_instance(1, 2)`，即`dec_instance.__call__(1, 2)`。而`dec_instance.__call__`則返回原先傳入的`self.func`搭配上`args = (1, 2)，kwargs = {}`這些參數的計算結果。

### 基本型態2（加上`__get__`）
`# 01`的`code`有個潛在問題，就是當它裝飾在`class`內的`function`時，如`01a`，會`raise TypeError`。
```python=
# 01a
class dec:
    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)


class MyClass:
    @dec
    def my_func(self, *args, **kwargs):
        pass
    
    
if __name__ == '__main__':
    my_inst = MyClass()
    my_inst.my_func()  # TypeError 
```
`01a`的錯誤訊息為`MyClass.my_func() missing 1 required positional argument: 'self'`。這是怎麼一回事呢？

我們一樣回到核心原理開始思考，雖然`MyClass`中的`my_func`原本是個`function`，但經過`dec`的裝飾後，`my_func`已經變作`dec_instance`，所以上述的`MyClass`可視為下面這個寫法的簡潔版（記得`@dec`是語法糖嗎？）。

```python=
# 01a
class MyClass:
    def my_func(self, *args, **kwargs):
        pass
    my_func = dec(my_func)
```
這麼一來，很清楚的看出`my_func`是位於`MyClass`中，由`dec`所建立的一個`dec_instance`。此時`my_inst.my_func()`，相當於`dec_instance`作為一個`callable`來呼叫`dec_instance.__call__()`，而其`__call__`需接收一個`self`參數，及選擇性給予的`*args`及`**kwargs`。由於我們沒有傳參數給`__call__`，所以Python提醒我們最少需要給`self`參數，才能呼叫成功。

或許您還是有疑惑，為什麼我們明明使用`my_inst.my_func()`，為什麼`my_inst`沒有自動傳遞給`my_func`，作為第一個參數`self`呢？那是因為`function`是一種`non-data descriptor`，其具備有`__get__`，並於其內使用`MethodType`來將`descriptor`的`instance`與呼叫其的`instance` `bound`在一起，所以才會有我們習慣的自動傳遞`instance`到`function`中，作為第一個參數`self`的行為。如果有些不明白的話，我們會於後續`導讀Descriptor HowTo Guide`的部份再詳談。

重點是，當使用`decorator class`裝飾`class`中的`function`，實作`__get__`可以讓它用起來，就像是一般的`instance method`（`註2`），如`# 02`。

```python=
# 02
from types import MethodType


class dec:
    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    def __get__(self, instance, owner_class):
        if instance is None:
            return self
        return MethodType(self, instance)


class MyClass:
    @dec
    def my_func(self, *args, **kwargs):
        pass


if __name__ == '__main__':
    my_inst = MyClass()
    my_inst.my_func()  # ok
```
`dec`的`__get__`中的`MethodType(self, instance)`會幫忙將`dec_instance`與`my_inst` `bound`在一起。

### 基本型態3（加上functools.update_wrapper）
`基本型態1`與`基本型態2`的寫法皆會喪失被裝飾`function`的`metadata`。一個折衷的辦法是將這些`metadata`更新到`dec_instance.__dict__`，即`__init__`中的`update_wrapper(self, self.func)`。

```python=
# 03
from functools import update_wrapper
from types import MethodType


class dec:
    def __init__(self, func):
        self.func = func
        update_wrapper(self, self.func)

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    def __get__(self, instance, owner_class):
        if instance is None:
            return self
        return MethodType(self, instance)
```



### 實例說明 
`# 04`透過`decorator`來`logging`一些資訊：
```python=
# 04
import logging
from functools import update_wrapper
from types import MethodType


class log:
    def __init__(self, func):
        self.func = func
        update_wrapper(self, self.func)

    def __call__(self, *args, **kwargs):
        logging.info(f'__call__ is called, {self.func=}, {args=}, {kwargs=}')
        return self.func(*args, **kwargs)

    def __get__(self, instance, owner_class):
        if instance is None:
            return self
        return MethodType(self, instance)


@log
def add(a: int, b: int) -> int:
    """Take two integers and return their sum."""
    return a + b


class MyClass:
    @log
    def add(self, a: int, b: int) -> int:
        """Take two integers and return their sum."""
        return a + b


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    my_inst = MyClass()
    print(add(1, 2))  # 3
    print(my_inst.add(1, 2))  # 3
```
在`__call__`中，我們加了一行`logging.info`來協助記錄每次`log`生成的`instance`被呼叫時，其實際使用的`func`、`args`及`kwargs`。
```
INFO:root:__call__ is called, self.func=<function add at 0x0000015CBE110C20>, args=(1, 2), kwargs={}
3
INFO:root:__call__ is called, self.func=<function MyClass.add at 0x0000015CBE88A160>, args=(<__main__.MyClass object at 0x0000015CBE884950>, 1, 2), kwargs={}
3
```
可以順便觀察`metadata`更新的狀況。
```
add=<__main__.log object at 0x0000015CBE4CF910>
add.__module__='__main__'
add.__name__='add'
add.__doc__='Take two integers and return their sum.'
add.__qualname__='add'
add.__annotations__={'a': <class 'int'>, 'b': <class 'int'>, 'return': <class 'int'>}
add.__dict__={'func': <function add at 0x0000015CBE110C20>, '__module__': '__main__', '__name__': 'add', '__qualname__': 'add', '__doc__': 'Take two integers and return their sum.', '__annotations__': {'a': <class 'int'>, 'b': <class 'int'>, 'return': <class 'int'>}, '__wrapped__': <function add at 0x0000015CBE110C20>}

my_inst.add=<bound method MyClass.add of <__main__.MyClass object at 0x0000015CBE884950>>
my_inst.add.__module__='__main__'
my_inst.add.__name__='add'
my_inst.add.__doc__='Take two integers and return their sum.'
my_inst.add.__qualname__='MyClass.add'
my_inst.add.__annotations__={'a': <class 'int'>, 'b': <class 'int'>, 'return': <class 'int'>}
my_inst.add.__dict__={'func': <function MyClass.add at 0x0000015CBE88A160>, '__module__': '__main__', '__name__': 'add', '__qualname__': 'MyClass.add', '__doc__': 'Take two integers and return their sum.', '__annotations__': {'a': <class 'int'>, 'b': <class 'int'>, 'return': <class 'int'>}, '__wrapped__': <function MyClass.add at 0x0000015CBE88A160>}
```

## decorator factory（本身可接收參數）
當我們希望有一個flag來控制這個`decorator`是否要`logging`，可以寫成`# 05`：
```python=
# 05
import logging
from functools import wraps


class log:
    def __init__(self, to_log=True):
        self.to_log = to_log

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if self.to_log:
                logging.info(
                    f'__call__ wrapper is called, {func=}, {args=}, {kwargs=}')
            return func(*args, **kwargs)
        return wrapper


@log()
def add(a: int, b: int) -> int:
    """Take two integers and return their sum."""
    return a + b


class MyClass:
    @log()
    def add(self, a: int, b: int) -> int:
        """Take two integers and return their sum."""
        return a + b


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    my_inst = MyClass()
    print(add(1, 2))  # 3
    print(my_inst.add(1, 2))  # 3
```
`decorator factory`一樣，可施加於一般`function`，及`class`內的`function`。

* `@log()`中的`log()`會先得到`log`的`instance`，稱作`log_instace`。由於`log`有實作`__call__`，所以`log_instace`為`callable`。
* 此時`@log()`相當於`@log_instance(add)`(`to_log`的資訊已傳至`self.to_log`)。由於`__call__`是一個`instance method`，`log_instance`將自動傳遞至`__call__`作為第一個參數`self`。
* 最後`__call__`會回傳`wrapper`，其接受參數與`add`相同，並會返回相同結果，只是額外針對`self.to_log`的值來決定是否進行`logging`。所以最終呼叫`add`相當於呼叫`wrapper`。
* 由於最終返回的是`wrapper` `function`，不再是基本型態中的`instance`，所以我們可以直接像在`decorator function`中一樣，使用較為方便的`functools.wraps`。

值得一提的是，這個情況我們不需替`log`實作`__get__`，即可施加於`class`內的`function`。原因是這次我們返回的是`wrapper`，其本身是`function`，`function`本身就有實作`__get__`，所以當使用`my_inst.add(1, 2)`，其會返回一個`bound`好`add`及`my_inst`的`MethodType` `instance`來接收`1`跟`2`這兩個參數。


### 實例說明
```python=
# 06
import logging
from functools import wraps
from numbers import Real
from typing import get_type_hints


class log:
    def __init__(self, *, to_log=True, validate_input=True):
        self.to_log = to_log
        self.validate_input = validate_input

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if self.to_log:
                logging.info(
                    f' `wrapper` is called, {func=}, {args=}, {kwargs=}')
            if self.validate_input:
                n = len(args) + len(kwargs)
                type_hints = get_type_hints(func)
                if n and n+1 > len(type_hints):  # return is included in type_hints
                    if self.to_log:
                        logging.error(
                            f'Annotations={type_hints}, {args=}, {kwargs=}')
                    raise TypeError('Some annotations might be missing.')

                if args and not all(isinstance(arg, type_)
                                    for arg, type_ in zip(args, type_hints.values())):
                    if self.to_log:
                        logging.error(
                            f'Annotations={type_hints}, {args=}, {kwargs=}')
                    raise TypeError(
                        f'Possible incorrect type assignment in {args=}')

                if kwargs and not all(isinstance(kw_value, type_)
                                      for name, type_ in type_hints.items()
                                      if (kw_value := kwargs.get(name))):
                    if self.to_log:
                        logging.error(
                            f'Annotations={type_hints}, {args=}, {kwargs=}')
                    raise TypeError(
                        f'Possible incorrect type assignment in {kwargs=}')

            result = func(*args, **kwargs)

            if self.validate_input:
                expected_return_type = type_hints['return']
                if not isinstance(result, expected_return_type):
                    logging.warning(
                        f' Return value: {result}(type={type(result)}) is not an '
                        f'instance of {expected_return_type}')
            if self.to_log:
                logging.info(' `wrapper` is finished.')
            return result
        return wrapper


@log(to_log=True, validate_input=True)
def add(a: Real, b: Real) -> Real:
    """Take two reals and return their sum."""
    return a + b


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    r = add(1.2, b=2.3)
    print(r, type(r))  # 3.5, float
```
```
INFO:root: `wrapper` is called, func=<function add at 0x0000024A7C3C4EA0>, args=(1.2,), kwargs={'b': 2.3}
INFO:root: `wrapper` is finished.
3.5 <class 'float'>
```
`# 06`與[[Day05]](https://ithelp.ithome.com.tw/articles/10317757)的`# 07`寫法不同的地方，只在：
* `# 06`將接收的參數邏輯放在`__init__`。
* `# 06`將`wrapper`放在`__call__`。

## 常用型態（@dec | @dec()）
如果想要同時能夠使用`@log`及`@log()`兩種語法，勢必要面對回傳值有時是`function`，有時是`instance`的情況，所以相關`metadata`的處理也要記得分開處理，我們做了一些嘗試（`註3`）。

相較之下，我們會建議使用一個`function`來包住一個`decorator class`，如`# 07`所示。原理其實和`decorator function`的`# 08`差不多。
```python=
# 07
import logging
from functools import wraps


class log:
    def __init__(self, *, to_log=True):
        self.to_log = to_log

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if self.to_log:
                logging.info(
                    f'__call__ wrapper is called, {func=}, {args=}, {kwargs=}')
            return func(*args, **kwargs)
        return wrapper


def logf(func=None, /, *, to_log=True):
    if func is None:
        return log(to_log=to_log)
    return log(to_log=to_log)(func)


@logf()
def add1(a: int, b: int) -> int:
    """Take two integers and return their sum."""
    return a + b


@logf
def add2(a: int, b: int) -> int:
    """Take two integers and return their sum."""
    return a + b


class MyClass:
    @logf()
    def add1(self, a: int, b: int) -> int:
        """Take two integers and return their sum."""
        return a + b

    @logf
    def add2(self, a: int, b: int) -> int:
        """Take two integers and return their sum."""
        return a + b


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    print(add1(1, 2))  # 3
    print(add2(1, 2))  # 3
    my_inst = MyClass()
    print(my_inst.add1(1, 2))  # 3
    print(my_inst.add2(1, 2))  # 3
```
若檢查所有`metadata`，也都有一起更新。
```python=
INFO:root:__call__ wrapper is called, func=<function add1 at 0x000001D48F3C4E00>, args=(1, 2), kwargs={}
3
INFO:root:__call__ wrapper is called, func=<function add2 at 0x000001D48F886200>, args=(1, 2), kwargs={}
3
INFO:root:__call__ wrapper is called, func=<function MyClass.add1 at 0x000001D48F8863E0>, args=(<__main__.MyClass object at 0x000001D48F8886D0>, 1, 2), kwargs={}
3
INFO:root:__call__ wrapper is called, func=<function MyClass.add2 at 0x000001D48F886520>, args=(<__main__.MyClass object at 0x000001D48F8886D0>, 1, 2), kwargs={}
3
```

## 當日筆記
*  使用`基本型態1`時，`decorator`可施加於一般的`function`。
*  使用`基本型態2`時，`decorator`可施加於一般的`function`及`class`內的`function`上。
*  使用`基本型態3`時，`decorator`可施加於一般的`function`及`class`內的`function`上，且被裝飾`function`的`metadata`會更新至`decorator`生成的`instance`內。
* `decorator factory`最終會返回的是`function`，其本身已具有`__get__`，所以不用額外處理。
* 使用`常用型態`時，建議使用一個`function`包住一個`decorator class`使用，我們覺得會比`註3`的寫法更簡單優雅。

## 備註
註1：當`class`內有實作`__call__`，該`class`生成的`instance`則為`callable`。

註2：其實對於`classmethod`或`staticmethod`上，`decorator class`也是可以用的，只是必須注意順序，要得先`@log`再加上`@classmethod`或`@staticmethod`。
```python=
# 101
class MyClass:
    @classmethod
    @log
    def class_method(cls):
        pass

    @staticmethod
    @log
    def static_method():
        pass
```
註3：`# 102`中，除了需要同時考慮兩種邏輯，還要記得實作`__get__`，相比於`# 07`的寫法複雜不少。

```python=
# 102
import logging
from functools import update_wrapper
from types import MethodType


class log:
    def __init__(self, func=None, /, *, to_log=True):
        self.func = func
        self.to_log = to_log
        if func is not None:
            update_wrapper(self, func)

    def _make_wrapper(self, func):
        def wrapper(*args, **kwargs):
            if self.to_log:
                logging.info(
                    f'__call__ inner is called, {func=}, {args=}, {kwargs=}')
            return func(*args, **kwargs)
        return wrapper

    def __call__(self, *args, **kwargs):
        if self.func is None:
            func = args[0]
            wrapper = self._make_wrapper(func)
            update_wrapper(wrapper, func)
            return wrapper
        else:
            func = self.func
            wrapper = self._make_wrapper(func)
            return wrapper(*args, **kwargs)

    def __get__(self, instance, owner_class):
        if instance is None:
            return self
        return MethodType(self, instance)
```

## Code
[本日程式碼傳送門](https://github.com/jrycw/py10wings/tree/master/src/02_decorator/day06_decorator_class)。