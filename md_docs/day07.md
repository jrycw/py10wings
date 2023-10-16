# [Day07] 次翼 - Decorator : @Func to Class
今天我們分享`decorator function`裝飾於`class`上的情況。本日接下來內容，會以`decorator`來作為`decorator function`的簡稱。

相較於[[Day05]](https://ithelp.ithome.com.tw/articles/10317757)與[[Day06]](https://ithelp.ithome.com.tw/articles/10317758)會回傳新的`function`或是`instance`，`Func @ Class`這種`function`裝飾`class`的情況，較多情況是`mutate`接收的`cls`並回傳，而不產生新的`class`。

至於實際上該如何使用呢?Python內建的``total_ordering``是一個絕佳的例子。今天我們先欣賞`total_ordering`的源碼後，再來做一個實例練習一下。

## `total_ordering`源碼
客製化`class`的排序是依靠各種`rich comparison`的`dunder method`。[total_ordering](https://docs.python.org/3/library/functools.html#functools.total_ordering)可以幫助我們在只實作`__lt__`、`__le__`、`__gt__`及 `__ge__`四種方法其中之一加上`__eq__`的情況下，使得客製化`class`能擁有所有`comparison`的功能。

* 首先Python定義一個`_convert` `dict`，以`__lt__`、`__le__`、`__gt__`及 `__ge__`四種方法的名稱為`key`，而`value`則為一個`list`內含三個`tuple`，代表剩餘三種需要由Python輔助完成的方法名稱及方法。

```python=
_convert = {
    '__lt__': [('__gt__', _gt_from_lt),
               ('__le__', _le_from_lt),
               ('__ge__', _ge_from_lt)],
    '__le__': [('__ge__', _ge_from_le),
               ('__lt__', _lt_from_le),
               ('__gt__', _gt_from_le)],
    '__gt__': [('__lt__', _lt_from_gt),
               ('__ge__', _ge_from_gt),
               ('__le__', _le_from_gt)],
    '__ge__': [('__le__', _le_from_ge),
               ('__gt__', _gt_from_ge),
               ('__lt__', _lt_from_ge)]
}
```
* 這些方法可以由數學上推論而得，我們舉`_gt_from_lt`為例，如何在有`__lt__`及`__eq__`（`註1`）的情況下推得`__gt__`。由Python註解可知`a > b`相當於`not (a < b)`及` a != b`的，而後者都是我們可以使用的方法。靠著已知的操作組合出新的`comparison`功能，`total_ordering`是不是相當巧妙的設計呢!
```python=
def _gt_from_lt(self, other):
    'Return a > b.  Computed by @total_ordering from (not a < b) and (a != b).'
    op_result = type(self).__lt__(self, other)
    if op_result is NotImplemented:
        return op_result
    return not op_result and self != other
```
* 最後我們觀察`total_ordering`內部實作邏輯。
    * 首先Python確認，我們「自己」實作了哪幾種不是由`object`繼承而來的`comparison`方法，然後將找到的方法名稱存在`roots`這個`set`內。如果沒有找到的話，代表我們連最少需要一種的要求都沒達到，則`raise ValueError`。
    * 接著如果有找到的話，Python會依照`__lt__ => __le__ => __gt__ => __ge__`的喜好順序，從`_convert`挑出剩下三種，有可能需要Python幫忙實作的方法。接著對這些方法打一個迴圈，如果方法名不在`roots`內，則使用`setattr`，將Python幫忙實作的方法，指給`cls`。這也代表Python的思維是，盡量使用「使用者實作的`comparison`」，除非沒有給予時，才給予幫助。
    * 最後回傳`cls`。

```python=
def total_ordering(cls):
    """Class decorator that fills in missing ordering methods"""
    # Find user-defined comparisons (not those inherited from object).
    roots = {op for op in _convert if getattr(cls, op, None) is not getattr(object, op, None)}
    if not roots:
        raise ValueError('must define at least one ordering operation: < > <= >=')
    root = max(roots)       # prefer __lt__ to __le__ to __gt__ to __ge__
    for opname, opfunc in _convert[root]:
        if opname not in roots:
            opfunc.__name__ = opname
            setattr(cls, opname, opfunc)
    return cls
```
### 注意事項
__理論上__ 您不需要實作`__eq__`，`total_ordering`也能提供一定程度的功能，因為`object`是預設有實作`__eq__`的。但`object`的`__eq__`預設是比較兩者是否為同一個`obj`，這可能不是您預期的行為。

`# 01`中：
* `p1`及`p2`是`Point`的`instance`，而`Point`實作有`__lt__`，`__eq__`並搭配`total_ordering`，這是一個標準的範例，所以`p1 == p2`會如預期是`True`。
* `p3`及`p4`是`PointWithoutCustomEq`的`instance`，而`PointWithoutCustomEq`只實作並搭配`total_ordering`，此時`p3 == p4`會是`False`，因為在`object`的`__eq__`判定兩個並不是同一個`obj`。的確兩個不是同一個`obj`，一個是`p3`，一個是`p4`，只是兩個`obj`都是由`PointWithoutCustomEq`生成而已。

```python=
# 01
from functools import total_ordering


@total_ordering
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __lt__(self, other):
        if isinstance(other, type(self)):
            return (self.x, self.y) < (other.x, other.y)
        return NotImplemented

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return (self.x, self.y) == (other.x, other.y)
        return NotImplemented


@total_ordering
class PointWithoutCustomEq:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __lt__(self, other):
        if isinstance(other, type(self)):
            return (self.x, self.y) < (other.x, other.y)
        return NotImplemented


if __name__ == '__main__':
    p1, p2 = Point(0, 0), Point(0, 0)
    print(p1 == p2)  # True

    p3, p4 = PointWithoutCustomEq(0, 0), PointWithoutCustomEq(0, 0)
    print(p3 == p4)  # False!!!
```

__所以實務上__ 還是建議依照Python docs的指示，自己實作`__eq__`。

## 實例說明
### 情境
假設您有一個個人的open source project，裡面實作了一些自己常用的小工具，其中有些重要的邏輯是要call [Rust](https://www.rust-lang.org/)或[Zig](https://ziglang.org/)來完成的。由於您對這兩種語言還在高速學習中，所以核心的程式碼常在變動。但好在使用者除了自己之外，就是同事等親朋好友，所以維護起來沒什麼大問題。突然有一天這個project被大神推薦了，使用者開始大量增加。雖然您有提供public interface給大家呼叫，但由於還在建置階段，支援的範圍不夠全面。此時，大家發現有些底層`Rust`或`Zig`實作的邏輯非常好用，可以直接呼叫，就不理會這是`underscore`開頭的`private function`，直接拿來用，結果就產生各式各樣的問題，塞爆您的github issue跟pull request。

於是您決定在某版本後，將這些部份打包成其它`library`，並從現在開始，當使用者呼叫這些函數時，報給他們`Deprecation Warning`。

這些需要報`Warning`的`function`都在`class`內且都是由`_call`開頭，您開始思考該怎麼樣完成這件事呢?
* 每個`function`都進去改 => 應該有更好的方法吧...
* 用`metaclasses`=> 但是某版本之後就不需要這個功能了，`metaclasses`會不會殺雞用牛刀了呢?
* ...

思考良久，您決定使用`decorator`來裝飾所有需要報`Warning`的`class`。這樣在某版本後，只要移除這些加上的`decorator`就好。

## 解題思路
* 總共需要寫兩個`decorator`:
    * 第一個命名為`my_warn`，是用來裝飾在`class`之上。
    * 第二個命名為`warn_using_private_func`，是用來裝飾在需要報`Warning`的`function`之上。

### my_warn實作
`my_warn`接收`cls`為變數，接下來我們對`cls.__dict__`打一個迴圈，如果該`obj`是`callable`且名字為`_call`開頭，則是我們要裝飾的對象（`註2`）。我們使用`setattr`重新將`cls.name`設定給裝飾過後的`obj`(即(`warn_using_private_func(obj)`)後，返回`cls`。
```python=
#02
def my_warn(cls):
    for name, obj in cls.__dict__.items():
        if callable(obj) and name.startswith('_call'):
            setattr(cls, name, warn_using_private_func(obj))
    return cls
```
### warn_using_private_func
`warn_using_private_func`是一個基本的`decorator function`，我們於真正呼叫底層`function`前(`fn(*args, **kwargs)`)，透過`warnings.warn`給出一個`DeprecationWarning`，並印出我們客製的訊息。

```python=
# 02
import warnings
from functools import wraps
from textwrap import dedent


def warn_using_private_func(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        warn_msg = dedent('''
            Users are discouraged from directly invoking this kind of private function 
            starting with `_call`, as it is scheduled for removal in version 0.51.''')
        warnings.warn(warn_msg, DeprecationWarning)
        return fn(*args, **kwargs)
    return wrapper
```

### 實際使用
```python=
#02

@my_warn
class MyClass:
    def _call_rust(self):
        '''This function will invoke some Rust code'''

    def _call_zig(self):
        '''This function will invoke some Zig code'''


if __name__ == '__main__':
    my_inst = MyClass()
    my_inst._call_rust()
    my_inst._call_zig()
```
直接將`my_warn`裝飾於`MyClass`上。此時，當我們使用`my_inst._call_rust()`或`my_inst._call_zig()`時，就會觸發`DeprecationWarning`。
```
/this/is/the/python/filepath/xxx.py DeprecationWarning: 
Users are discouraged from directly invoking this kind of private function 
starting with `_call`, as it is scheduled for removal in version 0.51..
  warnings.warn(warn_msg, DeprecationWarning)
```

如果您仔細觀察會發現，`DeprecationWarning`只出現一句。這其實是Python的設計，可以參考[Python docs](https://docs.python.org/3/library/warnings.html)。
> ... Repetitions of a particular warning for the same source location are typically suppressed. ...

事實上，這個設計的確是我們大部份情況下想要的行為。

`# 03`是使用繼承的情況，我們使用`warnings.simplefilter('always', DeprecationWarning)`來改變Python預設的行為，此時`Warning`會出現兩次，相信這不是您希望的行為。
```python=
# 03
...
# import及warn_using_private_func同`# 02`
warnings.simplefilter('always', DeprecationWarning)


@my_warn
class MyClass:
    def _call_rust(self):
        '''This function will invoke some Rust code'''


@my_warn
class MySubClass(MyClass):
    def _call_rust(self):
        '''This function will invoke some Rust code'''
        super()._call_rust()


if __name__ == '__main__':
    my_inst = MySubClass()
    my_inst._call_rust()  # warning message will show 2 times
```

## 備註
註1：由於[`__ne__`預設](https://docs.python.org/3/reference/datamodel.html#object.__ne__)為`__eq__`結果的相反，所以我們實際上是擁有三種`comparison method`。

註2：實務上，您可能要處理五花八門的型態，例如`property`、`class method`、`static method`及`class內的class`等等...。

## Code
[本日程式碼傳送門](https://github.com/jrycw/py10wings/tree/master/src/02_decorator/day07_decorating_class)。