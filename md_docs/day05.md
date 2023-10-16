# [Day05] 次翼 - Decorator : @Func to Func

## 次翼大綱
`decorator`為`meta programming`的技巧之一，可以改變被其裝飾`obj`之行為。

由於`decorator`可以用`function`及`class`兩種方法來實作，我們定義以
`function`實作的，稱為`decorator function`；而以`class`實作的，稱為`decorator class`。

又由於`decorator`可以裝飾在`function`或`class`上，所以可能會有以下四種組合:
1. `decorator function`裝飾於`function`上([[Day05]](https://ithelp.ithome.com.tw/articles/10317757)內容)。
2. `decorator function`裝飾於`class`上([[Day07]](https://ithelp.ithome.com.tw/articles/10317759)內容)。
3. `decorator class`裝飾於`function`上([[Day06]](https://ithelp.ithome.com.tw/articles/10317758)內容)。
4. `decorator class`裝飾於`class`上。

其中第四種`decorator class`裝飾於`class`上的使用情況，我們沒有想到適合的實例，所以決定只針對前三種`decorator`進行筆記。


本日接下來內容，會以`decorator`來作為`decorator function`的簡稱。


## 核心概念
`decorator`的核心概念為接受一個`function`，從中做一些操作，最後返回一個`function`。一般來說，返回的`function`會接收與原`function`相同的參數，並返回相同的結果，但卻能具有`decorator`額外賦予的功能(`註1`)。


## 原理
`decorator`的原理，可以用`# 01`來說明。

```python=
# 01
def dec(func):
    return func


def my_func():
    pass


if __name__ == '__main__':
    orig_func_id = id(my_func)
    my_func = dec(my_func)
    deced_func_id = id(my_func)
    print(orig_func_id == deced_func_id)  # True
```
* 定義一個`decorator`，名為`dec`。
* 定義一個待被裝飾的`function`，名為`my_func`。
* 定義一個變數，其名與`my_func`相同，來接收`dec(my_func)`的回傳值。

`dec`其實只是接收了一個變數`my_func`，再將其返回。比較特別的是，我們新定義了一個與被裝飾的`my_func`同名的變數來接收其回傳值。在這個範例裡，新變數`my_func`其實就是一開始定義的`my_func` `function`，這可以透過觀察前後兩個`my_func`的`id`確認。

## 語法糖
由於經常需要使用被裝飾的`function`名作為新變數名，Python提供了下列的`@dec`作為語法糖(`syntax suger`)，來幫助大家快速完成這類操作。因此，`# 01`可以改寫為`# 02`這個較常見的寫法:
```python=
# 02
def dec(func):
    return func


@dec
def my_func():
    pass
```

## 基本型態
### 基本型態1
觀察`# 02`，會發現`my_func`沒有接受任何參數，這使得它的應用有些局限。我們通常會希望`function`能根據不同的參數，給出相對應的結果。

根據上述期望，可以寫出`# 03`：
```python=
# 03
def dec(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


@dec
def my_func(*args: int, **kwargs: int) -> int:
    pass
```
* 定義一個`decorator`，名為`dec`。其接收一個`function`，但卻返回另一個於內部建立的`wrapper` `function`。
* 定義一個被`dec`裝飾的`function`，名為`my_func`，其可接受`*args`及`**kwargs`。

藉由`decorator`，`my_func`已經從原先的`my_func`變成`wrapper`這個`function`了。由於`wrapper`與原先的`my_func`接收相同的參數(即`*args`及`**kwargs`)，所以裝飾前後，`my_func`的呼叫方式是一致的。

當我們呼叫`my_func`時，實際上是在呼叫`wrapper`。舉例來說，此時的`my_func(1, 2)`，相當於呼叫`wrapper(1, 2)`。而`wrapper`則返回原先傳入的`my_func`搭配上`args = (1, 2)，kwargs = {}`這些參數的計算結果。

就`# 03`而言，不管`my_func`有沒有被`dec`裝飾，其結果是一樣的。但`decorator`可以視為一個hook，讓我們可以於函數呼叫前或後，進行一些操作。

### 基本型態2(加上`functools.wraps`)
如果仔細觀察一下`my_func`及其相關的`metadata`:
```
my_func=<function dec.<locals>.wrapper at 0x000001DBF55C4FE0>
my_func.__module__='__main__'
my_func.__name__='wrapper'
my_func.__doc__=None
my_func.__qualname__='dec.<locals>.wrapper'
my_func.__annotations__={}
my_func.__dict__={}
```
會發現`my_func`顯示為`wrapper`，且其`metadata`也不符合我們的預期，我們會希望即使是被裝飾過的`function`，其`metadata`還是可以保留。

Python內建的`functools.wraps`可以作為`decorator`使用(`註2`)，幫助我們更新正確的`metadata`至`wrapper` `function`，如`# 04`所示。
```python=
# 04
from functools import wraps


def dec(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


@dec
def my_func(*args: int, **kwargs: int) -> int:
    pass
```
```
my_func=<function my_func at 0x00000239ECC14FE0>
my_func.__module__='__main__'
my_func.__name__='my_func'
my_func.__doc__=None
my_func.__qualname__='my_func'
my_func.__annotations__={'args': <class 'int'>, 'kwargs': <class 'int'>, 'return': <class 'int'>}
my_func.__dict__={'__wrapped__': <function my_func at 0x00000239ECC16660>}
```

### 實例說明
一個常用的情況是透過`decorator`來`logging`一些資訊，如`# 05`:
```python=
# 05
import logging
from functools import wraps


def log(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logging.info(f'wrapper is called, {func=}, {args=}, {kwargs=}')
        return func(*args, **kwargs)
    return wrapper


@log
def add(a: int, b: int) -> int:
    return a + b


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    print(add(1, 2))  # 3
```
在`wrapper`中，我們加了一行`logging.info`來協助記錄每次`wrapper`被呼叫時，其實際使用的`func`、`args`及`kwargs`。

此時若呼叫`add`，會顯示logging的記錄，且返回正確答案。
```
INFO:root:wrapper is called, func=<function add at 0x000001E918BC6660>, args=(1, 2), kwargs={}
3
```

## decorator factory(本身可接收參數)
由於我們希望裝飾前後的函數，會接收相同的參數，如此較為方便使用。所以當想要傳入一些自訂的參數或是flag時，可以將其作為`decorator`本身的參數傳入。

舉例來說，當我們想要有一個flag來控制這個`decorator`是否要`logging`，可以寫成`# 06`:
```python=
# 06
import logging
from functools import wraps


def log(to_log=True):
    def dec(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if to_log:
                logging.info(f'wrapper is called, {func=}, {args=}, {kwargs=}')
            return func(*args, **kwargs)
        return wrapper
    return dec


@log(to_log=False)
def add(a: int, b: int) -> int:
    """Take two integers and return their sum."""
    return a + b
```
`log`這個`function`內又包了兩層`function`，乍看好像有點複雜，讓我們逐層拆解看看。
* 首先，`log`接收一個參數，名為`to_log`，其預設值為`True`，並會返回內部第一層的`dec` `function`。此時，對於被裝飾的`function`來說，相當於我們直接將`dec`裝飾其上，並將給定的`to_log`往下傳遞。
* 接下來，我們就像回到`基本型態`，`dec`接收一個`func`(即`add`)，並返回`wrapper` `function`。
* 最後，於`wrapper`內，實作大部份邏輯。此時，於`wrapper`中我們擁有:
    * 第一層接收的`to_log`參數。
    * 第二層接收的被裝飾的`add` `function`。
    * 第三層接收的`add`參數(`*args`及`**kwargs`)。此時，我們利用`to_log`來決定是否進行`logging`，並將呼叫`add(*args, **kwargs)`的結果作為`wrapper`的返回值。

這樣的pattern，可以稱為`decorator factory`，因為實際上`dec`才是`decorator`，第一層的參數只是為了提供真正的`decorator`一些額外的訊息。


### 實例說明
`# 07`為一個`decorator factory`實例。
```python=
# 07
import logging
from functools import wraps
from numbers import Real
from typing import get_type_hints


def log(*, to_log=True, validate_input=True):
    def dec(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if to_log:
                logging.info(
                    f' `wrapper` is called, {func=}, {args=}, {kwargs=}')
            if validate_input:
                n = len(args) + len(kwargs)
                type_hints = get_type_hints(func)
                if n and n+1 > len(type_hints):  # return is included in type_hints
                    if to_log:
                        logging.error(
                            f'Annotations={type_hints}, {args=}, {kwargs=}')
                    raise TypeError('Some annotations might be missing.')

                if args and not all(isinstance(arg, type_)
                                    for arg, type_ in zip(args, type_hints.values())):
                    if to_log:
                        logging.error(
                            f'Annotations={type_hints}, {args=}, {kwargs=}')
                    raise TypeError(
                        f'Possible incorrect type assignment in {args=}')

                if kwargs and not all(isinstance(kw_value, type_)
                                      for name, type_ in type_hints.items()
                                      if (kw_value := kwargs.get(name))):
                    if to_log:
                        logging.error(
                            f'Annotations={type_hints}, {args=}, {kwargs=}')
                    raise TypeError(
                        f'Possible incorrect type assignment in {kwargs=}')

            result = func(*args, **kwargs)

            if validate_input:
                expected_return_type = type_hints['return']
                if not isinstance(result, expected_return_type):
                    logging.warning(
                        f' Return value: {result}(type={type(result)}) is not an ' +
                        f'instance of {expected_return_type}')
            if to_log:
                logging.info(' `wrapper` is finished.')
            return result
        return wrapper
    return dec


@log(to_log=True, validate_input=True)
def add(a: Real, b: Real) -> Real:
    """Take two reals and return their sum."""
    return a + b


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    r = add(1.2, b=3.2)
    print(r, type(r))  # 3.5, float
```
```
INFO:root: `wrapper` is called, func=<function add at 0x000002D40BB3CFE0>, args=(1.2,), kwargs={'b': 2.3}
INFO:root: `wrapper` is finished.
3.5 <class 'float'>
```
* 第一層`log`接收兩個`keyword-only arguments`，`to_log`及`validate_input`，預設皆為`True`。當`to_log`為`True`時，會呼叫`logging`模組，記錄不同等級的資訊，如`logging.info`，`logging.warning`及`logging.error`等等。當`validate_input`為`True`，會確認給定的`args`、`kwargs`及計算結果與`type hint`是否相符(`註3`)。最後會回傳第二層的`dec` `function`。
* 第二層的`dec` `function` 會接收被裝飾的`function`為參數，即`func`。最後會回傳第三層的`wrapper` `function`。
* 第三層的`wrapper`會接收使用者呼叫`func`的參數，即`*args`及`**kwargs`。我們將`functools.wraps`裝飾於`wrapper`上，讓其幫忙將`func`的`metadata`更新給`wrapper`。
* 接下來我們對`wrapper`逐段說明。
    * 如果`to_log`為`Ture`，則呼叫`logging.info`記錄`wrapper`被呼叫。
    * 如果`validate_input`為`True`，將會分別確認三件事。如果其中任何一件事不符合，則會呼叫`logging.error`並`raise TypeError`。
        * 首先，我們呼叫`types.get_type_hints`來取得`func`的`type hint`，接著確認是不是每個參數與回傳值都有給定`annotation`。
        * 再來，由於使用者呼叫`add`時，可能會使用`positional`或`keyword`兩種型態傳遞參數，所以要分別確認`args`及`kwargs`。
        * 由於`args`必定會出現於`kwargs`之前，再加上Python於3.7後，其`dict`會維持插入時的順序(3.6屬於非正式支援)，所以我們可以使用`zip(args, type_hints.values())`搭配`isinstance`來確認`args`內的每個`obj`都是`type_hints`內所描述`type`的`instance`(`註4`)。
        * 針對`kwargs`，我們可以試著尋找`kwargs`與`type_hints`的共同`key`，並搭配`isinstance`確認這些共同`key`的`value`皆為`type_hints`內所描述型態的`instance`。
    * `result = func(*args, **kwargs)`是`func`真正被呼叫，進行計算的地方。
    * 如果`validate_input`為`Ture`，則檢查`result`是否為給定`type hint`的`instance`。此時，即便是未通過檢查，也僅呼叫`logging.warning`，而不`raise TypeError`。這是一個折衷的寫法，一般來說如果`result`能順利計算完畢，相比於`raise Exception`，我們會傾向回傳所計算結果，但以`warning`提醒，讓使用者自己確認，究竟是給錯型態，又或者結果真的不符預期。
    * 如果`to_log`為`Ture`，呼叫`logging.info`記錄`wrapper`執行完畢。
    * 最後回傳`result`。

## 常用型態(@dec | @dec())
如果依照上述的寫法，我們需要呼叫`decorator factory`，才能取得真正的`decorator`，也就是說即使我們沒有要修改`decorator factory`的預設值，我們仍然需要使用`@log()`的語法才能裝飾`function`，使用起來有點麻煩。

**我們的目標是，希望在沒有要修改`decorator factory`預設值時，能夠僅使用`@log`，且`@log`與`@log()`是同義的。**

要能夠達成目標的關鍵是，如何區分第一個參數是`decorator factory`的參數，還是已經是要被裝飾的`function`。這可以仰仗Python的`positional-only argument`及`keyword-only argument`。我們可以指定第一個參數一定要是`positional-only`(預設值為`None`)，而第二個參數以後一定要是`keyword-only`。

如此一來，我們可以判斷當第一個參數為`None`時，是使用了`@log()`這種語法；而當其不為`None`時，表示是接收了要被裝飾的`function`，即使用了`@log`這種語法。

`decorator function`的寫法，除了可以裝飾於`function`上，也適用於`class`中的`function`。

以下提供兩種常見的寫法：
### 方法1
```python=
# 08
import logging
from functools import wraps


def log(func=None, /, *, to_log=True):
    def dec(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if to_log:
                logging.info(f'wrapper is called, {func=}, {args=}, {kwargs=}')
            return func(*args, **kwargs)
        return wrapper

    if func is None:
        return dec
    return dec(func)


@log()
def add1(a: int, b: int) -> int:
    """Take two integers and return their sum."""
    return a + b


@log
def add2(a: int, b: int) -> int:
    """Take two integers and return their sum."""
    return a + b


class MyClass:
    @log()
    def add1(self, a: int, b: int) -> int:
        """Take two integers and return their sum."""
        return a + b

    @log
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
```
INFO:root:wrapper is called, func=<function add1 at 0x0000029A770C6980>, args=(1, 2), kwargs={}
3
INFO:root:wrapper is called, func=<function add2 at 0x0000029A770C6660>, args=(1, 2), kwargs={}
3
INFO:root:wrapper is called, func=<function MyClass.add1 at 0x0000029A772A62A0>, args=(<__main__.MyClass object at 0x0000029A77167810>, 1, 2), kwargs={}
3
INFO:root:wrapper is called, func=<function MyClass.add2 at 0x0000029A772A6200>, args=(<__main__.MyClass object at 0x0000029A77167810>, 1, 2), kwargs={}
3
```
`方法1`較為直觀，以`func`是否為`None`來決定回傳值。


### 方法2
```python=
# 09
import logging
from functools import partial, wraps


def log(func=None, /, *, to_log=True):
    if func is None:
        return partial(log, to_log=to_log)

    @wraps(func)
    def wrapper(*args, **kwargs):
        if to_log:
            logging.info(f'wrapper is called, {func=}, {args=}, {kwargs=}')
        return func(*args, **kwargs)
    return wrapper


@log()
def add1(a: int, b: int) -> int:
    """Take two integers and return their sum."""
    return a + b


@log
def add2(a: int, b: int) -> int:
    """Take two integers and return their sum."""
    return a + b


class MyClass:
    @log()
    def add1(self, a: int, b: int) -> int:
        """Take two integers and return their sum."""
        return a + b

    @log
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
```
INFO:root:wrapper is called, func=<function add1 at 0x000002607BBC67A0>, args=(1, 2), kwargs={}
3
INFO:root:wrapper is called, func=<function add2 at 0x000002607BBC4FE0>, args=(1, 2), kwargs={}
3
INFO:root:wrapper is called, func=<function MyClass.add1 at 0x000002607C0862A0>, args=(<__main__.MyClass object at 0x000002607BA98950>, 1, 2), kwargs={}
3
INFO:root:wrapper is called, func=<function MyClass.add2 at 0x000002607C0863E0>, args=(<__main__.MyClass object at 0x000002607BA98950>, 1, 2), kwargs={}
3
```
`方法2`的寫法非常優雅，且可以免去定義一層中間的`function`，但需要對`decorator`有較深的體會才容易運用自如(`註5`)。

## 當日筆記
* 不論`decorator`包含了幾層`function`，我們的目的可以想作是返回一個`wrapper` `function`，其所接收的參數與返回值，會與被裝飾的`function`相同，而我們可以在過程中動點手腳，例如進行`logging`或驗證型別等。

當在多層`function`中迷路時，建議回到核心原理，以`# 08`的架構逐層往下思考。
```python=
@log(to_log=False)
def add(a: int, b: int) -> int:
    return a + b
```
相當於
```python=
add = log(to_log=False)(add)
```
相當於 
```python=
add = dec(add) 
```
`dec`中內含`to_log=False`。

相當於 
```python=
add = wrapper
```
`wrapper`中內含`to_log=False`及`func`為`add`，且`functools.wraps`會幫忙將`add`的`metadata`更新給`wrapper`。

此時的`add`就是`wrapper`，所以`add(1, 2)`即相當於`wrapper(1, 2)`。
* `functools.wraps`可以快速將`基本型態1`轉為`基本型態2`。
* `常用型態` `方法1`直觀但比較繁瑣，`方法2`稍難理解但優雅。

## 備註
註1：由於`decorator`是`meta programming`的一種，所以我們可以返回任何`obj`。舉例來說，雖然很奇怪，但是我們是可以將`args`中每一項加1之後，再傳遞給`func`。
```python=
# 101
from functools import wraps


def dec(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        args = (arg+1 for arg in args)
        return func(*args, **kwargs)
    return wrapper


@dec
def add(a: int, b: int) -> int:
    return a + b


if __name__ == '__main__':
    print(add(1, 2))  # 5
```

註2：[`functools.wraps`](https://docs.python.org/3/library/functools.html#functools.wraps)會呼叫[`functools.update_wrapper`](https://docs.python.org/3/library/functools.html#functools.update_wrapper)來更新`metadata`，如果有除了預設的`__module__`, `__name__`, `__qualname__`, `__doc__`,`__annotations__`及`__dict__`的`attribute`需要更新的話，必須自己呼叫`functools.update_wrapper`或是手動更新。

註3：如果您有很多參數或有類似`json`、`database`等有`schema`需要驗證的情形，以`Rust`重新改寫的[`PydanticV2`](https://docs.pydantic.dev/latest/)或許會是不錯的選擇。

註4：從Python3.10開始，[`isinstance`可以接收多種`Union Type`](https://docs.python.org/3/library/functions.html#isinstance)，也就是說`isinstance(1, type.Union[int, str])`、`isinstance(1, int | str)`或是`# isinstance(1, (int, str))`等，都是可接受的語法。

註5：對於想更深入研究`# 09`寫法的朋友，可以參考[這篇文章](https://pybit.es/articles/decorator-optional-argument/)。
註6：`*args`與`**kwargs`的[type hints](https://adamj.eu/tech/2021/05/11/python-type-hints-args-and-kwargs/)。

## Code
[本日程式碼傳送門](https://github.com/jrycw/py10wings/tree/master/src/02_decorator/day05_decorator_function)。